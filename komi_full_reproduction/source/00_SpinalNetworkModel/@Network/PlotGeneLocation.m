function PlotGeneLocation(obj,Genes,Plotstyle,varargin)
    load("01_SpinalGeometryFiles\matLayers.mat")
    GreyMat =  find(strcmpi(matLayers.lowres,'grey')); 
    Coord = obj.Genetics.Coords(GreyMat,:);
    CountSpatial = obj.Genetics.Counts(:,GreyMat);
    GenesSpatial = obj.Genetics.Genes;
    %%
    G = GenesSpatial(contains(string(GenesSpatial),Genes));
    %% Pre Compute GeneMap borders
    [Xmin,Xmax]= bounds(obj.Genetics.Coords.x);
    [Ymin,Ymax] = bounds(obj.Genetics.Coords.y);
    X = Xmin:Xmax;
    Y = Ymin:Ymax;
    [Xm,Ym] = meshgrid(X,Y);
    [Xs,Ys] = meshgrid(Xmin:Xmax,Ymin:Ymax);
    %% Make ZeroMap
    for i = 1:length(G(:))
       lig = G(i);
       ligind = GenesSpatial == lig;
       if(nnz(ligind))
           Map = zeros([length(Y),length(X)]);
           CRD = table2array(Coord(:,2:3));   
           Mcrd = CRD;% + round(normrnd(0,10,size(CRD)),0);
           for ii = 1:length(Mcrd)
               ym = Y == Mcrd(ii,2);
               xm = X == Mcrd(ii,1);
               Map(ym,xm) = CountSpatial(ligind,ii);
           end
           Vind =~ isnan(Map);
           Val = Map(Vind);
           MapPlot = griddata(Xm(Vind),Ym(Vind),Val,Xm,Ym,'natural');
           MapPlot(isnan(MapPlot)) = 0;
           if(obj.isSymetric)
              MapPlot = (MapPlot+fliplr(MapPlot))/2;
           end
           MapPlot = moransI(MapPlot,ones(15,15));
           if(contains(Plotstyle,{'Contour','Heatmap'}))
               MapPlot = imgaussfilt(MapPlot,15);
           end
           fig = figure;
           colormap("bone")
           if(contains(Plotstyle,{'Contour'}))
                MapPlot(MapPlot>0) = log2(MapPlot(MapPlot > 0)./mean(MapPlot(MapPlot > 0)));
                [M,c] = contourf(MapPlot,[1 1]);
           else
                imagesc(MapPlot)
           end
           set(gca,'YDir','reverse')
           colorbar
           %caxis([0 1]);
           title(string(lig)) 
       end
    end   
end