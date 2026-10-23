function PlotTransitionRandomStructured(N,varargin)
    screensize = get(groot,'ScreenSize');
    InitPos = rand(size(N.Position));
    EndPos = N.Position;
    Pos = InitPos;
    S = N.Rates+10;
    S(S==0) = nan;
    Speed = 0.00005;
    noise_ample = 0.0005;    
    VA =[-180,0];
    t1 = 10;
    t2 = 3000;
    Save = 0;
    Mpos = mean(N.Position,1);

    for ii = 1:2:length(varargin)
        switch varargin{ii}
            case 'SavePath'
                SavePath = varargin{ii+1};
                Save = 1;
            case 'SaveName'
                Name = varargin{ii+1};
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
    
    DorPop = unique(N.Types(N.Layers == 'DRG'|N.Layers == '1Sp'| N.Layers == '2Sp0' | N.Layers == '2SpI' | N.Layers == '3Sp' | N.Layers == '4Sp'),'sorted');
    VentrPop = unique(N.Types(N.Layers == '5Spm'|N.Layers == '5SpL'| N.Layers == '6SpM' | N.Layers == '6SL' | N.Layers == '7Sp' | N.Layers == '8Sp' | N.Layers == 'D' | N.Layers == '10Sp' | N.Layers == 'Ps9'),'sorted');
    MN = unique(N.MnID(~isundefined(N.MnID)));

    cmapdorsal = fliplr(autumn(length(DorPop)));  %# Creates a 6-by-3 set of colors from the HSV colormap   
    cmapmn = sky(length(MN)); 

    C = zeros(size(N.ConnMat,1),3);
    for T = 1:length(DorPop)
        whr = N.Types == DorPop(T);
        C(whr,:) = repmat(cmapdorsal(T,:),[nnz(whr),1]);
    end
    
    for T = 1:length(VentrPop)
        whr = N.Types == VentrPop(T);
        switch VentrPop(T)
            case 'V2a-1'
               C(whr,:) = repmat(Colors().V2a_1,[nnz(whr),1]);
            case 'V2a-2'
               C(whr,:) = repmat(Colors().V2a_2,[nnz(whr),1]);
            case 'V2b'
               C(whr,:) = repmat(Colors().V2b,[nnz(whr),1]);
            case 'V1'
               C(whr,:) = repmat(Colors().V1,[nnz(whr),1]);
            case 'V3'
                C(whr,:) = repmat(Colors().V3,[nnz(whr),1]);
            case 'V0d'
                C(whr,:) = repmat(Colors().V0d,[nnz(whr),1]);
            case 'V0v'
                C(whr,:) = repmat(Colors().V0v,[nnz(whr),1]);
            case 'DI6'
                C(whr,:) = repmat(Colors().DI6,[nnz(whr),1]);
            case 'MN' 
                C(whr,:) = repmat(Colors().MN,[nnz(whr),1]);
        end
    end  

    for T = 1:length(MN)
        whr = N.MnID == MN(T);
        C(whr,:) = repmat(cmapmn(T,:),[nnz(whr),1]);
    end

    fig = figure(Color=Colors().BergBlack,Position=screensize);
    ax1 = axes();
    axis off equal tight
    box off
    view(VA(1),VA(2))
    xlim([-20 max(N.Position(:,2))+20])
    hold on
    %% Switch from a random network to a spatial network
    % for j = 1:3:length(N.Rates)
    %     f1 = scatter3(ax1,Pos(:,1),Pos(:,2),Pos(:,3),0.65.*S(j,:)',C,'filled','MarkerFaceAlpha',0.75);
    %     drawnow
    %     if(Save)
    %        f = getframe(fig);
    %        writeVideo(v,f);
    %     end
    %     %% Update Position 
    %     if(j>t1)
    %         Pos = Pos + (EndPos-Pos)*Speed;% + normrnd(0.,noise_ample,[size(Pos)]);
    %     end
    %     if(j>t2)
    %         view([VA(1)-(90/(length(N.Rates)-t2))*(j-t2) VA(2)+(90/(length(N.Rates)-t2))*(j-t2)])
    %     end
    %     delete(f1);
    % end
    view([-270 90]);
    % %% Bring All neurons to same size
    S1 = 0.5.*S(end,:)';
    Size(:) =  S1(:) - 5*(0.5.*S(end,:)'- 2)./5;
    shpwm=alphaShape(N.Geometry.Position((N.Geometry.Type=="WM"),1),N.Geometry.Position((N.Geometry.Type=="WM"),2),N.Geometry.Position((N.Geometry.Type=="WM"),3),1000);
    shpgm=alphaShape(N.Geometry.Position(~(N.Geometry.Type=="WM"|N.Geometry.Layers(:,3)=="DRG"),1),N.Geometry.Position(~(N.Geometry.Type=="WM"|N.Geometry.Layers(:,3)=="DRG"),2),N.Geometry.Position(~(N.Geometry.Type=="WM"|N.Geometry.Layers(:,3)=="DRG"),3),148);
    plot(shpwm,"EdgeColor","none","FaceColor",Colors().BergWhite,'FaceAlpha',0.1,'FaceLighting','gouraud','BackFaceLighting','lit','EdgeLighting','gouraud')
    for ll = 1:0.1:5
        if(Save)
           f = getframe(fig);
           writeVideo(v,f);
        end
    end
    T2 = text(Mpos(:,1),Mpos(:,2),'Rostro-caudal Synapse Distributions','FontSize',25,'Color',[1 1 1],'FontWeight','bold',VerticalAlignment='bottom');
    for w = 1:10:600
         if(Save)
          f = getframe(fig);
          writeVideo(v,f);
          end
    end
    %% Display Properties of individual populations
    dis = 1;
    ii = 1;
    for T = unique(N.Types)'
        whr = (N.Types == T) & N.Segment=='L5';
        Mp = mean(N.Position(whr,:),1);
        SizeT = Size; 
        SizeT(whr) = SizeT(whr) + 50;
        for w = 1:15:600
           if(Save)
                f = getframe(fig);
                writeVideo(v,f);
            end
        end
        if(dis)
            delete(T2);
            dis = 0;
        end
        f1 = scatter3(ax1,N.Position(:,1),N.Position(:,2),N.Position(:,3),SizeT/3,C,'filled','MarkerFaceAlpha',0.2); 
        hold on 
        T1 = text(Mp(:,1),Mp(:,2),T,'FontSize',40,'Color',[1 1 1],'FontWeight','bold');
        for w = 1:15:600
           if(Save)
                f = getframe(fig);
                writeVideo(v,f);
            end
        end        
        H(ii) = GenerateDistribPlot(N,whr,mean(C(whr,:),1),0.9);
        ii = ii+1;
        delete(T1);
    end    
    for w = 1:5:600
       if(Save)
            f = getframe(fig);
            writeVideo(v,f);
        end
    end    
    K = GenerateDistribPlot(N,N.Segment=='L5',Colors().BergWhite,0);
    for w = 1:15:600
        for jj = 1:length(H)
           alpha(H(jj),0.85*(1-w/700));
           alpha(K,w/700);
        end
        if(Save)
          f = getframe(fig);
          writeVideo(v,f);
        end
    end   
    if(Save)
       f = getframe(fig);
       writeVideo(v,f);
       close(v)
    end
end

function h = GenerateDistribPlot(N,whr,C,trans)
    ConnMat = N.ConnMat;
    Ex =  N.Transmit > 0;
    In =  N.Transmit < 0;
    ProjEx =  sum(ConnMat(:,whr&Ex),2); 
    ProjIn =  sum(ConnMat(:,whr&In),2); 
    L = round(N.Position(:,2),-2);
    edges = [min(L):100:max(L)];
    yin = discretize(N.Position(logical(ProjIn),2), edges);
    yex = discretize(N.Position(logical(ProjEx),2), edges);
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
    h = barh(edges(1:end-1), -25*(abs(MExZ.*CExZ)-abs(MInZ.*CInZ)),'FaceColor',C,'FaceAlpha',trans,'EdgeColor','none','ShowBaseLine','off','FaceColorMode','manual');
end




% L = round(range(N.Position(:,2)),-2);
% edges = [-L:100:L];
% 

% fig = figure(Position=screensize);
% subplot (2,3,1)
% bar(edges(1:end-1), -abs(MInZ.*CInZ),'FaceColor',[Colors().BergOrange],'FaceAlpha',0.5);
% hold on
% bar(edges(1:end-1), abs(MExZ.*CExZ),'FaceColor',[Colors().BergElectricBlue],'FaceAlpha',0.5);