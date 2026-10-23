function SimulateAxonProp(obj,varargin)
    %% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%% SET PARAMETERS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    PopOfI = ones(size(obj.Types));
    LayerOfI = ones(size(obj.Layers));
    LatOfI =  ones(size(obj.Latera));
    TransOfI = ones(size(obj.Transmit));
    MNOfI = ones(size(obj.MnID));
    FEOfI = ones(size(obj.FlexExtID));
    SegOfI = ones(size(obj.Segment));
    UoI = ones(size(obj.Segment));
    C = NaN;
    for ii = 1:2:length(varargin)
        switch varargin{ii}
            case 'Type'
               PopOfI = contains(string(obj.Types),varargin{ii+1});
               popi = varargin{ii+1};
            case 'Layer'
               LayerOfI = contains(string(obj.Layers),varargin{ii+1});
            case 'Latera'
               LatOfI = obj.Latera == varargin{ii+1};
            case 'Transmit'
               TransOfI = obj.Transmit == varargin{ii+1};
            case 'MnID'
               MNOfI = obj.MnID == varargin{ii+1};
            case 'FlexExt'
               FEOfI = obj.FlexExtID == varargin{ii+1};
            case 'Segment'
               SegOfI = contains(string(obj.Segment),varargin{ii+1});           
            case 'SaveName'
                Name = varargin{ii+1};
            case 'UoI'
                UoI = varargin{ii+1};
            case 'Color'
                C = varargin{ii+1};
        end
    end   
    Sources = PopOfI&LayerOfI&LatOfI&TransOfI&MNOfI&FEOfI&SegOfI&UoI;
    % Axon Growth Simulation Parameters
    it = 1000; % Number of iterations of simulations
    GrowthRate = 0.02;
    PosNoise = 0.08; %sqrt(DiffusionKernelWidthSR); % Noise on position (randon walk)

    % Video Related Parameters
    DisplayVid = 'on';
    isVideo = 0;
    mkdir(['./Videos']);
    v = VideoWriter(['./Videos' filesep 'AxonsProp']);
    v.FrameRate = 30;
    v.Quality = 50;
    if(isVideo)
        open(v);
        DisplayVid = 'off';
    end
    %% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%% Select Points of pop with higher diff expression in space %%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Populate postion Matrices for further computations
    pos = repmat(obj.Position(Sources,:),[1 1]);
    ixs = repmat(find(Sources),[1 1]);
    ors = sign(randn(size(Sources)));
    % Populate inital trajectory 
    Iin =  normrnd(0,PosNoise,size(pos));
    %% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%% Run Simulation and Plot Trajectories %%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
    DorPop = unique(obj.Types(obj.Layers == 'DRG'|obj.Layers == '1Sp'| obj.Layers == '2Sp0' | obj.Layers == '2SpI' | obj.Layers == '3Sp' | obj.Layers == '4Sp'),'sorted');
    VentrPop = unique(obj.Types(obj.Layers == '5Spm'|obj.Layers == '5SpL'| obj.Layers == '6SpM' | obj.Layers == '6SL' | obj.Layers == '7Sp' | obj.Layers == '8Sp' | obj.Layers == 'D' | obj.Layers == '10Sp' | obj.Layers == 'Ps9'),'sorted');
    MN = unique(obj.MnID(~isundefined(obj.MnID)));

    cmapdorsal = fliplr(autumn(length(DorPop)));  %# Creates a 6-by-3 set of colors from the HSV colormap   
    cmapmn = sky(length(MN)); 
    cmap = zeros(size(obj.ConnMat,1),3);

    if isnan(C)
    for T = 1:length(DorPop)
        whr = obj.Types == DorPop(T);
        cmap(whr,:) = repmat(cmapdorsal(T,:),[nnz(whr),1]);
    end
    
    for T = 1:length(VentrPop)
        whr = obj.Types == VentrPop(T);
        switch VentrPop(T)
            case 'V2a-1'
               cmap(whr,:) = repmat(Colors().V2a_1,[nnz(whr),1]);
            case 'V2a-2'
               cmap(whr,:) = repmat(Colors().V2a_2,[nnz(whr),1]);
            case 'V2b'
               cmap(whr,:) = repmat(Colors().V2b,[nnz(whr),1]);
            case 'V1'
               cmap(whr,:) = repmat(Colors().V1,[nnz(whr),1]);
            case 'V3'
                cmap(whr,:) = repmat(Colors().V3,[nnz(whr),1]);
            case 'V0d'
                cmap(whr,:) = repmat(Colors().V0d,[nnz(whr),1]);
            case 'V0v'
                cmap(whr,:) = repmat(Colors().V0v,[nnz(whr),1]);
            case 'DI6'
                cmap(whr,:) = repmat(Colors().DI6,[nnz(whr),1]);
            case 'MN' 
                cmap(whr,:) = repmat(Colors().MN,[nnz(whr),1]);
        end
    end  

    for T = 1:length(MN)
        whr = obj.MnID == MN(T);
        cmap(whr,:) = repmat(cmapmn(T,:),[nnz(whr),1]);
    end
    else
        cmap = repmat(C,[size(cmap,1),1]);
    end

    screensize = get(groot,'ScreenSize');
    fig = figure('Color','black','Position',[0,0,screensize(3)/2, screensize(4)]);
    set(fig, 'Visible',DisplayVid);    

    % ptCloudIn = pointCloud(obj.Position);
    % [mesh,radii] = pc2surfacemesh(ptCloudIn,"poisson");

    shpwm=alphaShape(obj.Geometry.Position((obj.Geometry.Type=="WM"),1),obj.Geometry.Position((obj.Geometry.Type=="WM"),2),obj.Geometry.Position((obj.Geometry.Type=="WM"),3),1000);
    shpgm=alphaShape(obj.Geometry.Position(~(obj.Geometry.Type=="WM"|obj.Geometry.Layers(:,3)=="DRG"),1),obj.Geometry.Position(~(obj.Geometry.Type=="WM"|obj.Geometry.Layers(:,3)=="DRG"),2),obj.Geometry.Position(~(obj.Geometry.Type=="WM"|obj.Geometry.Layers(:,3)=="DRG"),3),148);

    plot(shpwm,"EdgeColor","none","FaceColor",Colors().V2a_1,'FaceAlpha',0.05,'FaceLighting','gouraud','BackFaceLighting','lit','EdgeLighting','gouraud')
    hold on
    %plot(shpgm,"EdgeColor","none","FaceColor",Colors().BergGray02,'FaceAlpha',0.15,'FaceLighting','gouraud','BackFaceLighting','lit','EdgeLighting','gouraud')
    axis off 
    hold on 
    scatter3(obj.Position(Sources,1),obj.Position(Sources,2),obj.Position(Sources,3),20,Colors().BergWhite,'filled','MarkerFaceAlpha',1,'MarkerEdgeColor','none'); %
    set(gca, 'Color','none')
    axis equal tight off

    C = zeros(it,3,size(pos,1));
    Col = zeros(3,size(pos,1));
    % 
    for tt = 1:it
        Z = [];
        for pp = 1:size(pos,1)
            Targets = logical(obj.ConnMat(:,ixs(pp)));
            Coord = pos(pp,:);
            Dist = obj.Position(Targets,:)-Coord;   
            if(ors(ixs(pp))>0)
                Dist(Dist(:,2)<0,:) = [];
            else
                Dist(Dist(:,2)>0,:) = [];
            end
            C(tt,:,pp) = Coord;
            Col(:,pp) = cmap(ixs(pp),:);
            update = sum([pos(pp,:);mean(GrowthRate.*Dist ,1) + normrnd(0,100*PosNoise,[1 size(Dist,2)])],1); 
            pos(pp,:) = update;
        end
        s1 = plot3(squeeze(C(1:tt,1,:)),squeeze(C(1:tt,2,:)),squeeze(C(1:tt,3,:)));
        colororder(fig,Col');
        drawnow;
        %view([90 90])
        if(tt<it)
        delete(s1);
        end
        if(isVideo)
            f = getframe(fig);
            writeVideo(v,f);
        end
    end
    if(isVideo)
        close(v);
    end
end