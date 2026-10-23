function PlotRaster(obj,varargin)
    sig = 0.1;
    srt = 1;
    M = 10 ;
    P = 0:size(obj.Rates,2)-1;
    UoI = true(1,size(obj.ConnMat,1));
    Side = 'R';
    for ii = 1:2:length(varargin)
        switch varargin{ii}
            case 'sigma'
               sig = varargin{ii+1};
            case 'sort'
               srt = varargin{ii+1};
            case 'UoI'
               UoI = varargin{ii+1};
        end
    end

    if(srt)
       % [~,ix] = sort(obj.Position(:,3));
       ix = ComputeFiringPhaseSorting(obj.Rates(2000:end,:));
    else 
        ix = randperm(size(obj.ConnMat,1));
    end

    UoI = UoI(ix);
    RI = obj.Rates(1000:end,ix)';
    RI = RI(UoI,:);

    RIsp = ((RI-min(RI,[],2))+5);
    RIsp = RIsp./(max(RIsp,[],2));
    Poiss = poissrnd(RIsp/50,size(RIsp));
    SpikeTrain = logical(Poiss);

    figure 
    for i = 1:size(SpikeTrain,1)
      indices = find(SpikeTrain(i,:));
      scatter(indices,SpikeTrain(i,indices) + P(i),M,'MarkerFaceColor',Colors().BergGray09,'MarkerFaceAlpha',0.9,'MarkerEdgeColor','none');
      hold on
    end
end