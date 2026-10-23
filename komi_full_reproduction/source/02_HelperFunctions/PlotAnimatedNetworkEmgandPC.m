function PlotAnimatedNetworkEmgandPC(N,varargin)
    screensize = get(groot,'ScreenSize'); 
    Save = 0;
    W = N.ConnMat;
    Save = 0;
    RS = 1;
    VA =[-130,50];
    EPos = nan;
    CC = nan;
    trail = 300;
    noiselevel= 0.2;
    pad = 750;
    srt = 1;
    M = 10 ;
    P = 0:size(N.Rates,2)-1;
    Proj = 0;
    Source = true(1,size(N.Rates,2));
    UoI = true(1,size(N.ConnMat,1));
    Moi = categorical({'Iliopsoas','Quadriceps','Vastus Lateralis','Biceps Femoris','Tibialis Anterior','Gastrocnemius'});
   

    for ii = 1:2:length(varargin)
        switch varargin{ii}
            case 'SavePath'
                SavePath = varargin{ii+1};
                Save = 1;
            case 'SaveName'
                Name = varargin{ii+1};
            case 'MN'
               Moi = categorical(varargin{ii+1})';
            case 'sort'
               srt = varargin{ii+1};
            case 'UoI'
               UoI = varargin{ii+1};
            case 'ElectrodePos'
                EPos =varargin{ii+1};
            case 'Cluster_chan'
                CC = varargin{ii+1};
            case 'Source'
                Source = varargin{ii+1};
            case 'Project'
                Proj = varargin{ii+1};
        end
    end

    if (Save)
          if ~exist(SavePath, 'dir')
            mkdir(SavePath)
          end 
    v = VideoWriter([SavePath '/ ' Name],"MPEG-4");
    v.FrameRate = 30;
    v.Quality = 60;
    open(v);
    end

    if(isempty(N.EstimatedRates))
        N.ComputeEstimatedRates;
    end

    if(isempty(N.PC))
        N.ComputePC('Estimated',1,'Source',Source);
    end
    

    DorPop = unique(N.Types(N.Layers == 'DRG'|N.Layers == '1Sp'| N.Layers == '2Sp0' | N.Layers == '2SpI' | N.Layers == '3Sp' | N.Layers == '4Sp'),'sorted');
    VentrPop = unique(N.Types(N.Layers == '5Spm'|N.Layers == '5SpL'| N.Layers == '6SpM' | N.Layers == '6SL' | N.Layers == '7Sp' | N.Layers == '8Sp' | N.Layers == 'D' | N.Layers == '10Sp' | N.Layers == 'Ps9'),'sorted');
    MN = unique(N.MnID(~isundefined(N.MnID)));

    cmapdorsal = fliplr(autumn(length(DorPop)));  
    cmapventralex = flipud(cool(length(VentrPop))); 
    cmapventralin = cool(length(VentrPop));
    cmapmn = sky(length(MN)); 

    C = zeros(size(N.ConnMat,1),3);
    for T = 1:length(DorPop)
        whr = N.Types == DorPop(T);
        C(whr,:) = repmat(cmapdorsal(T,:),[nnz(whr),1]);
    end
    
    for T = 1:length(VentrPop)
        whr = N.Types == VentrPop(T);
        if(mean(N.Transmit(whr)) < 0)
            C(whr,:) = repmat(cmapventralin(T,:),[nnz(whr),1]);
        else 
            C(whr,:) = repmat(cmapventralex(T,:),[nnz(whr),1]);
        end
    end  

    for T = 1:length(MN)
        whr = N.MnID == MN(T);
        C(whr,:) = repmat(cmapmn(T,:),[nnz(whr),1]);
    end

    %% Compute EMG signal
    jj = 1;
    EMG = [];
    MoI = categorical();
    Col = [];
    for ii = fliplr(Moi)
       ix = N.MnID==ii & N.Latera > 0;
       if(~nnz(ix))
           continue
       end
       MoI(jj) = ii;
       Col(jj,:) = mean(C(ix,:),1);
       prob = sum(N.Rates(:,ix),2);
       sig = randn(size(prob))*noiselevel.*binornd(1,normcdf(normalize(prob,'zscore')));
       sig = sig.*prob/5  + (randn(size(prob))*noiselevel) ;
       EMG(:,jj) = [(randn(1,pad)*noiselevel) (sig*noiselevel)'] + 10*jj;
       jj = jj+1;
    end
    %% Compute Raster 
    if(srt)
        ix = ComputeFiringPhaseSorting(N.Rates(Source,:));
    else 
        [~,ix] = sort(N.Position(:,3));
    end

    UoI = UoI(ix);
    RI =  N.Rates(1:end,ix);
    RIsp = ((RI-min(RI,[],1)));
    RIsp = RIsp./(max(RIsp,[],1));
    Poiss = poissrnd(RIsp/40,size(RIsp));
    SpikeTrain = [zeros(pad,size(Poiss,2)); logical(Poiss)];

    Rates = GetGaussianFiring(SpikeTrain,50,1000); 
    RatesS = Rates(pad+1:end,:);
    RatesS(RatesS==0) = nan;

    SpikeTrain = SpikeTrain(:,UoI);
    location = N.Position(ix,:);
    if(any(~isnan(CC),"all")&&any(~isnan(EPos),"all")&&Proj)
        CC = CC(ix);
        location = [EPos(CC,1) EPos(CC,2) EPos(CC,3)];
    end

    if(Proj)
        UoIp = UoI;
    else
        UoIp = true(1,size(N.ConnMat,1));
    end

    %% Compute online gain
    L = round(range(N.Position(:,2)),-2);
    edges = [-L:250:L];
    tau_V = ones(size(N.ConnMat,1),1)*50;% Slower Excitation
    tau_V(sum(N.ConnMat,1) < 0 & ~(N.Types=='MN')',:) = 25; % Faster Inhibition
    g = abs(diff(movmean(RatesS,10,1),1,1));
    g = movmean(g,500,1);
    g = flipud(movmean(flipud(g),500,1));
    g = (100./tau_V').*g;
    ConnMat= N.ConnMat;
    ConnMatIpsiOr(N.Latera < 0,N.Latera > 0) = 0;
    ConnMatIpsiOr(N.Latera > 0,N.Latera < 0) = 0;
    ConnMatContraOr = N.ConnMat;
    ConnMatContraOr(N.Latera > 0,N.Latera > 0) = 0;
    ConnMatContraOr(N.Latera < 0,N.Latera < 0) = 0;
%%
    fig = figure(Color=Colors().BergBlack,Position=screensize);
    %% Define Ax1
    ax1 = subplot(3,3,[1 2 4 5 7 8]); % For the 3D
    axis off equal tight
    box on
    view(VA(1),VA(2))
    hold on
    %% Define Ax2
    ax2 = subplot(3,3,3); % For the PC
    axis off equal
    box off
    set(ax2,'Color','none')
    xlim([min(N.PC(:,1)) max(N.PC(:,1))]);
    ylim([min(N.PC(:,2)) max(N.PC(:,2))]);
    zlim([min(N.PC(:,3)) max(N.PC(:,3))]);
    view(-20,-30)
    hold on
    plot3(ax2,[ax2.XLim(1) ax2.XLim(1)],[ax2.YLim(1) ax2.YLim(1)],[ax2.ZLim]-(ax2.ZLim(1)),'Color',Colors().BergWhite,'LineWidth',2);
    plot3(ax2,[ax2.XLim(1) ax2.XLim(1)],[ax2.YLim],[0 0],'Color',Colors().BergWhite,'LineWidth',2);
    plot3(ax2,[ax2.XLim],[ax2.YLim(1) ax2.YLim(1)],[0 0],'Color',Colors().BergWhite,'LineWidth',2);
    title('PCA','FontSize',20,'FontWeight','bold','Color',Colors().BergWhite)

    %% Definee Ax4
    ax4 = subplot(3,3,6); % For the EMG
    axis on square
    set(ax4,'Color','none')
    set(ax4,'YColor',Colors().BergWhite)
    box on
    hold on
    xlim([0 2*pad]);
    ylim([-15 nnz(UoI)+15]);
    plot(ax4,[pad pad],ax4.YLim,'Color',Colors().BergWhite,'LineWidth',2);
    jj = 1;
    yticks([]);
    title('Raster','FontSize',20,'FontWeight','bold','Color',Colors().BergWhite)

    %% Definee Ax3
    ax3 = subplot(3,3,9); % For the EMG
    axis on square
    set(ax3,'Color','none')
    set(ax3,'YColor',Colors().BergWhite)
    box on
    hold on
    xlim([0 1500]);
    ylim([-15 10*size(EMG,2)+15]);
    plot(ax3,[750 750],ax3.YLim,'Color',Colors().BergWhite,'LineWidth',2);
    jj = 1;
    yticks([1:length(MoI)]*10);
    yticklabels(MoI);
    title('EMG','FontSize',20,'FontWeight','bold','Color',Colors().BergWhite)

   % %% Define Ax5 
   % ax5 = subplot(3,3,7);
   % xlim([-L L])
   % ylim([-300 300])
   % axis off
   % hold on
   % %% Define Ax6
   %  ax6 =  subplot(3,3,8);
   %  axis off
   %  hold on
   %  linkaxes([ax5 ax6]);
    %%
    if(~isnan(EPos))
        scatter3(ax1,EPos(:,1),EPos(:,2),EPos(:,3),20,'Marker','square','MarkerEdgeColor',Colors().BergWhite,'MarkerFaceColor',Colors().BergGray05,'MarkerFaceAlpha',0.4,'LineWidth',0.01,'MarkerEdgeAlpha',0.4);
        hold on
    end
    scatter3(ax1,N.Geometry.Position(N.Geometry.Type=="WM",1),N.Geometry.Position(N.Geometry.Type=="WM",2),N.Geometry.Position(N.Geometry.Type=="WM",3),'filled','MarkerFaceAlpha',0.05,'MarkerEdgeColor','none','MarkerFaceColor',Colors().BergGray02);
    for nn = 1:5
        for ii = 1:33:size(RatesS,1)
            f1 = scatter3(ax1,location(UoIp,1),location(UoIp,2),location(UoIp,3),2*RatesS(ii,UoIp),C(UoIp,:),'filled','MarkerFaceAlpha',0.75);
            f2 = plot3(ax2,N.PC(max(1,ii-trail):ii,1),N.PC(max(1,ii-trail):ii,2),N.PC(max(1,ii-trail):ii,3),'LineWidth',4,'Color',sky(1));
            f3 = plot(ax3,circshift(EMG,-ii));
            ConnMatIspi = g(ii,:).*ConnMatIpsiOr;
            % ConnMatContra = g(ii,:).*ConnMatContraOr;
            % diffipsi = GeneratePlot(N,ConnMatIspi,edges);
            % diffcontra= GeneratePlot(N,ConnMatContra,edges);
            % p1 = plot(ax5,edges(1:end-1),diffipsi,'Color',[Colors().BergWhite 0.2],'LineWidth',2);
            % p2 = plot(ax6,edges(1:end-1),diffcontra,'Color',[Colors().BergWhite 0.2],'LineWidth',2);
            if(~isempty(Col))
                colororder(ax3,Col);
            end
            ST = circshift(SpikeTrain,-ii)';
            [ri,ci] = find(ST(:,1:2*pad));
            f4 = scatter(ax4,ci,ri,M,'MarkerFaceColor',Colors().BergGray02,'MarkerFaceAlpha',0.9,'MarkerEdgeColor','none');
            drawnow;
            if(Save)
                f = getframe(fig);
                writeVideo(v,f);
            else
                pause(0.033/RS);
            end        
            delete(f1);
            delete(f2);
            delete(f3);
            delete(f4);     
            % delete(p1);
            % delete(p2);
        end
    end
    if(Save)
        f = getframe(fig);
        writeVideo(v,f);
        close(v)
    end
end

function difference = GeneratePlot(N,ConnMat,edges)
    Ex =  N.Transmit > 0;
    In =  N.Transmit < 0;
    Dist = bsxfun(@minus,N.Position(:,2),N.Position(:,2)');
    ProjEx = ConnMat(:,Ex); 
    ProjIn = ConnMat(:,In);
    DistEx = Dist(:,Ex);
    DistIn = Dist(:,In);
    
    yin = discretize(DistIn(ProjIn~= 0), edges);
    yex = discretize(DistEx(ProjEx~= 0), edges);
    [GnIn,Min,Cin] = grpstats(ProjIn(ProjIn~=0), yin,["gname","mean","numel"]);
    [GnEx,Mex,Cex] = grpstats(ProjEx(ProjEx~=0), yex,["gname","mean","numel"]);
    MInZ = zeros(length(edges)-1,1);
    MExZ = zeros(length(edges)-1,1);
    CInZ = zeros(length(edges)-1,1);
    CExZ = zeros(length(edges)-1,1);
    MInZ(str2double(GnIn)) = Min;
    MExZ(str2double(GnEx)) = Mex;
    CInZ(str2double(GnIn)) = Cin;
    CExZ(str2double(GnEx)) = Cex;
    difference = abs(MExZ.*CExZ)-abs(MInZ.*CInZ);
end
 