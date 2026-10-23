function PlotDynamicsConnection3D(axs,Network,R,varargin)
    location = Network.Position;
    W = Network.ConnMat;
    Save = 0;
    Col = nan;
    for ii = 1:2:length(varargin)
        switch varargin{ii}
            case 'SavePath'
                SavePath = varargin{ii+1};
                Save = 1;
            case 'SaveName'
                Name = varargin{ii+1};
            case 'Color'
                Col = varargin{ii+1};
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

    pheno = sign(sum(W,1));

    axes(axs)
    axis equal
    hold on
    C =(abs(W)/max(abs(W(W~=0)),[],'all')).^3;
    for ii = 1:33:size(R,2)
        if(isnan(Col))
            f1 = scatter3(axs,location(pheno>0,1),location(pheno>0,2),location(pheno>0,3),R(pheno>0,ii),Colors().BergOrange,'filled','MarkerFaceAlpha',0.1);
            f2 = scatter3(axs,location(pheno<0,1),location(pheno<0,2),location(pheno<0,3),R(pheno<0,ii),Colors().BergElectricBlue,'filled','MarkerFaceAlpha',0.3);
            f3 = scatter3(axs,location(Network.Types=="MN",1),location(Network.Types=="MN",2),location(Network.Types=="MN",3),R(Network.Types=="MN",ii),Colors().BergYellow,'filled','MarkerFaceAlpha',0.3);
        else
            f1 = scatter3(axs,location(:,1),location(:,2),location(:,3),R(:,ii),Colors().BergWhite,'filled','MarkerFaceAlpha',0.75);
            %colormap('hsv');
            %caxis([0 1])
        end
        drawnow;
       
        fig = gcf;
        if(Save)
            f = getframe(fig);
            writeVideo(v,f);
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
 