function PlotRates(obj,varargin)
    PopOfI = ones(size(obj.Types));
    LayerOfI = ones(size(obj.Layers));
    LatOfI =  ones(size(obj.Latera));
    TransOfI = ones(size(obj.Transmit));
    MNOfI = ones(size(obj.MnID));
    FEOfI = ones(size(obj.FlexExtID));
    SegOfI = ones(size(obj.Segment));
    UoI = ones(size(obj.Segment));
    Est = 0;
    for ii = 1:2:length(varargin)
        switch varargin{ii}
            case 'Type'
               PopOfI = contains(string(obj.Types),varargin{ii+1});
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
            case 'Estimated'
                Est = varargin{ii+1};
        end
    end   
    figure 
    if(Est)
        if(isempty(obj.EstimatedRates))
            obj.ComputeEstimatedRates;
        end
        plot(obj.EstimatedRates(:,PopOfI&LayerOfI&LatOfI&TransOfI&MNOfI&FEOfI&SegOfI&UoI));
    else
        plot(obj.Rates(:,PopOfI&LayerOfI&LatOfI&TransOfI&MNOfI&FEOfI&SegOfI&UoI));
    end
end