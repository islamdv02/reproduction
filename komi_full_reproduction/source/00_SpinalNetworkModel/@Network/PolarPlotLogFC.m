function PolarPlotLogFC(obj,Gene,varargin)
     load("03_SpinalCordGeneticsFiles\matCellInfo.mat");
     Groups = unique(obj.Types)';
     for ii = 1:2:length(varargin)
        switch varargin{ii}
            case 'Groups'
               Groups = categorical(varargin{ii+1});
        end
     end   
    
    jj = 1;
    CountSingleCell = obj.Genetics.CountsSC(contains(string(obj.Genetics.GenesSC),string(Gene)),:);
    for PopOfInterest = Groups
            whr = CellTypesCensus.Type == PopOfInterest;
            poptar = ismember(obj.Genetics.LineageSC,CellTypesCensus.PutativeLineage(whr));
            % Compute Log Fold Change versus all other population
            Wght = mean(CountSingleCell(:,poptar),'all');
            WghtRest = mean(CountSingleCell(:,~poptar),'all');
            log2fc(jj) = log2(Wght./WghtRest);
            jj = jj+1;
    end

    Prop = log2fc;
    Prop(Prop<0) =0 ;
    Theta =[90 90+(180/(length(Prop)-1)).*(1:(length(Prop)-1))];
    polarplot(deg2rad([Theta Theta(1)]),[Prop Prop(1)])
    rlim([0 round(max(log2fc),1)+0.1]);
    thetaticks(Theta);
    thetaticklabels(Groups);
end
