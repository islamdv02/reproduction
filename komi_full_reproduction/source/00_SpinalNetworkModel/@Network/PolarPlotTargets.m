function PolarPlotTargets(obj,UoI,varargin)
     Groups = unique(obj.Types);
     for ii = 1:2:length(varargin)
        switch varargin{ii}
            case 'Groups'
               Groups = varargin{ii+1};
        end
    end   
    Types = obj.Types(UoI);
    [N,Cat] = histcounts(Types);
    [Ntot,Cattot] = histcounts(obj.Types);
    [~,whr] = ismember(Groups,Cat);
    [~,whrtot] = ismember(Groups,Cattot);
    Prop = N(whr)./Ntot(whrtot);
    Theta =[90 90+(180/(length(Prop)-1)).*(1:(length(Prop)-1))];
    polarplot(deg2rad([Theta Theta(1)]),[Prop Prop(1)])
    rlim([0 1]);
    thetaticks(Theta);
    thetaticklabels(Groups);
end
