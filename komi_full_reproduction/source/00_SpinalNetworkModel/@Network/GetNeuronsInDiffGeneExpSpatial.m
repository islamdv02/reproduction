function UoI = GetNeuronsInDiffGeneExpSpatial(obj,Genes,varargin)
    load("01_SpinalGeometryFiles\matGeometry.mat")
    LogFC = 1;
    Source = 'Network';
    for ii = 1:2:length(varargin)
        switch varargin{ii}
            case 'LogFCThreshold'
                LogFC = varargin{ii+1};
            case 'Source'
               Source = varargin{ii+1};
    end
    GreyMat =  find(strcmpi(matLayers.lowres,'grey')); 
    WhiteMat =  find(strcmpi(matLayers.lowres,'white')); 
    WMCoord = obj.Genetics.Coords(WhiteMat,:);
    Coord = obj.Genetics.Coords(GreyMat,:);
    CountSpatial = obj.Genetics.Counts(:,GreyMat);
    GenesSpatial = obj.Genetics.Genes;
    convfactor = 3500/range(obj.Genetics.Coords.x);
    %%
    G = GenesSpatial(contains(string(GenesSpatial),Genes));
    %% Pre Compute GeneMap borders
    [Xmin,Xmax]= bounds(WMCoord.x);
    [Ymin,Ymax] = bounds(WMCoord.y);
    X = Xmin:Xmax;
    Y = Ymin:Ymax;
    [Xm,Ym] = meshgrid(X,Y);
    %% Make ZeroMap
    if(strcmpi(Source,'Network'))
        UoI = false(size(obj.Position(:,1)));
    elseif(strcmpi(Source,'Geometry'))
        UoI = false(size(obj.Geometry.Position(:,1)));
    end
    for jj = 1:length(G)
        lig = G(jj);
        ligind = GenesSpatial == lig;
        Map = zeros([length(Y),length(X)]);
        CRD = table2array(Coord(:,2:3));   
        Mcrd = CRD;
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
        MapPlot = imgaussfilt(MapPlot,15);
        MapPlot = log2(MapPlot./mean(MapPlot(MapPlot > 0)));
        M = contourc((X-mean(WMCoord.x)),-(Y-min(WMCoord.y)),MapPlot,[LogFC LogFC]);
        [~,loc] = findpeaks(abs(diff(M(1,:),2)),'MinPeakHeight',10);
        M(:,[1 loc]) = NaN;
        M = M.*convfactor;
        if(strcmpi(Source,'Network'))
            UoI = UoI | inpolygon(obj.Position(:,1),obj.Position(:,3),M(1,2:end),M(2,2:end));
        elseif(strcmpi(Source,'Geometry'))
            UoI = UoI | inpolygon(obj.Geometry.Position(:,1),obj.Geometry.Position(:,3),M(1,2:end),M(2,2:end));
        end
    end
    if(strcmpi(Source,'Network'))
        scatter(obj.Position(~UoI,1),obj.Position(~UoI,3),"filled",'MarkerFaceColor',Colors().BergBlack,MarkerFaceAlpha=0.5)
        hold on 
        scatter(obj.Position(UoI,1),obj.Position(UoI,3),"filled",'MarkerFaceColor',Colors().BergElectricBlue,MarkerFaceAlpha=0.5)
        hold on 
    elseif(strcmpi(Source,'Geometry'))    
        scatter(obj.Geometry.Position(~UoI,1),obj.Geometry.Position(~UoI,3),"filled",'MarkerFaceColor',Colors().BergBlack,MarkerFaceAlpha=0.5)
        hold on 
        scatter(obj.Geometry.Position(UoI,1),obj.Geometry.Position(UoI,3),"filled",'MarkerFaceColor',Colors().BergElectricBlue,MarkerFaceAlpha=0.5)
        hold on 
    end
    plot(polyshape(M(1,:),M(2,:)));
    axis equal tight off
end