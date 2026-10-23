function UoI = GetGenesDiffExpSingleCell(obj,Genes,varargin)
    LogFC = 1;
    RM = 0;
    for ii = 1:2:length(varargin)
        switch varargin{ii}
            case 'LogFCThreshold'
                LogFC = varargin{ii+1};
            case 'RobustMean'
                RM = 1;
    end
    load("03_SpinalCordGeneticsFiles\matCellInfo.mat");
    CountSingleCell = obj.Genetics.CountsSC(contains(string(obj.Genetics.GenesSC),string(Genes)),:);
    UoI = false(size(obj.Types));
    T = unique(obj.Types,'stable');
    for PopOfInterest = T'
        whr = CellTypesCensus.Type == PopOfInterest;
        poptar = ismember(obj.Genetics.LineageSC,CellTypesCensus.PutativeLineage(whr));
        % Compute Log Fold Change versus all other population
        if(RM)
            Wght = quantile(CountSingleCell(:,poptar),3,2);
            Wght = (Wght(:,2)/2)+((sum(Wght(:,[1 3]),2))/4);
            WghtRest = quantile(CountSingleCell(:,~poptar),3,2);
            WghtRest = (WghtRest(:,2)/2)+((sum(WghtRest(:,[1 3]),2))/4);
        else 
            Wght = mean(CountSingleCell(:,poptar),'all');
            WghtRest = mean(CountSingleCell(:,~poptar),'all');
        end
        log2fc = log2(Wght./WghtRest);
        % Compute Wilcoxon rank test for pop/the rest
        WghtSC = CountSingleCell(:,poptar);
        WghtRestSC = CountSingleCell(:,~poptar);
        pval = [];
        for ii = 1:size(WghtSC,1)
            try
                pval(ii) = ranksum(WghtSC(ii,:),WghtRestSC(ii,:));
            catch
                pval(ii) = 0;
            end
        end
        % Select differentially expressed genes
        signif = (log2fc > LogFC) & (pval' < 0.05); 
        UoI(obj.Types == PopOfInterest) = any(signif);
    end
    scatter(obj.Geometry.Position(obj.Geometry.Type=="WM",1),obj.Geometry.Position(obj.Geometry.Type=="WM",3),'filled','MarkerFaceAlpha',0.2,'MarkerEdgeColor','none','MarkerFaceColor',[Colors().BergGray02]);
    hold on 
    scatter(obj.Position(~UoI,1),obj.Position(~UoI,3),"filled",'MarkerFaceColor',Colors().BergBlack,MarkerFaceAlpha=0.5)
    scatter(obj.Position(UoI,1),obj.Position(UoI,3),"filled",'MarkerFaceColor',Colors().BergElectricBlue,MarkerFaceAlpha=0.5)
    axis equal tight
end