function AnimatedPlotRates(obj,varargin)
    screensize = get(groot,'ScreenSize');
    location = obj.Position;
    W = obj.ConnMat;
    Save = 0;
    Col = nan;
    RS = 1;
    VA =[-250,70];
    uoi = 0;
    UoI = true(size(W,1),1);
    EPos = nan;
    for ii = 1:2:length(varargin)
        switch varargin{ii}
            case 'SavePath'
                SavePath = varargin{ii+1};
                Save = 1;
            case 'SaveName'
                Name = varargin{ii+1};
            case 'Color'
                Col = varargin{ii+1};
            case 'Axe'
                axs = varargin{ii+1};
            case 'ReplaySpeed'
                RS = varargin{ii+1};
            case 'ViewAngle'
                VA = varargin{ii+1};
            case 'UoI'
                UoI =varargin{ii+1};
                uoi = 1;
            case 'ElectrodePos'
                EPos =varargin{ii+1};
        end
    end

    if (Save)
          if ~exist(SavePath, 'dir')
            mkdir(SavePath)
          end 
    v = VideoWriter([SavePath '/ ' Name],"MPEG-4");
    v.FrameRate = 30;
    v.Quality = 50;
    open(v);
    end

    pheno = obj.Transmit;
    In = pheno< 0 ; 
    Ex = pheno > 0;
    Rates = obj.Rates; 
    Rates(Rates==0) = nan;

    fig = figure(Color=Colors().BergBlack,Position=screensize);

    if(~isnan(EPos))
        scatter3(EPos(:,1),EPos(:,2),EPos(:,3),20,'Marker','square','MarkerEdgeColor',Colors().BergWhite,'MarkerFaceColor',Colors().BergGray05,'MarkerFaceAlpha',0.4,'LineWidth',0.01,'MarkerEdgeAlpha',0.4);
        hold on
    end

    scatter3(obj.Geometry.Position(obj.Geometry.Type=="WM",1),obj.Geometry.Position(obj.Geometry.Type=="WM",2),obj.Geometry.Position(obj.Geometry.Type=="WM",3),'filled','MarkerFaceAlpha',0.05,'MarkerEdgeColor','none','MarkerFaceColor',Colors().BergGray02);
    axis off equal
    box on
    axis vis3d
    rotate3d
    view(VA(1),VA(2))
    axis equal
    hold on
    axs = gca;
    
    p1 = [0 0 500];                         % First Point
    p2 = [0 max(obj.Position(:,2)) 500];                         % Second Point
    dp = p2-p1;                         % Difference
    quiver3(p1(1),p1(2),p1(3),dp(1),dp(2),dp(3),0,"filled",'LineWidth',3,'Color',Colors().BergWhite)
    C =(abs(W)/max(abs(W(W~=0)),[],'all')).^3;
    for ii = 1:33:size(Rates,1)
        if(isnan(Col))
            f1 = scatter3(axs,location(Ex&UoI,1),location(Ex&UoI,2),location(Ex&UoI,3),Rates(ii,Ex&UoI),Colors().BergElectricBlue,'filled','MarkerFaceAlpha',0.1);
            f2 = scatter3(axs,location(In&UoI,1),location(In&UoI,2),location(In&UoI,3),Rates(ii,In&UoI),Colors().BergOrange,'filled','MarkerFaceAlpha',0.3);
            f3 = scatter3(axs,location(obj.Types=="MN"&UoI,1),location(obj.Types=="MN"&UoI,2),location(obj.Types=="MN"&UoI,3),Rates(ii,obj.Types=="MN"&UoI),Colors().BergYellow,'filled','MarkerFaceAlpha',0.3);
        else
            f1 = scatter3(axs,location(UoI,1),location(UoI,2),location(UoI,3),Rates(ii,UoI),Colors().BergWhite,'filled','MarkerFaceAlpha',0.75);
        end
        drawnow;
       
        if(Save)
            f = getframe(fig);
            writeVideo(v,f);
        else
            pause(0.033/RS);
        end        
        if(isnan(Col))
            delete(f1);
            delete(f2);
            delete(f3);
        else
            delete(f1);
        end
    end
    if(Save)
        close(v)
    end
end
 