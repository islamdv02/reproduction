function GenerateSynapticDistrib(obj,varargin)
    PopOfI = ones(size(obj.Types));
    LayerOfI = ones(size(obj.Layers));
    LatOfI =  ones(size(obj.Latera));
    TransOfI = ones(size(obj.Transmit));
    MNOfI = ones(size(obj.MnID));
    FEOfI = ones(size(obj.FlexExtID));
    SegOfI = ones(size(obj.Segment));
    pop = '';

    for ii = 1:2:length(varargin)
        switch varargin{ii}
            case 'Type'
               pop = varargin{ii+1};
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
        end
    end   
    whr = PopOfI&LayerOfI&LatOfI&TransOfI&MNOfI&FEOfI&SegOfI;

    switch pop
        case 'V2a-1'
           C = Colors().V2a_1;
        case 'V2a-2'
           C = Colors().V2a_2;
        case 'V2b'
           C = Colors().V2b;
        case 'V1'
           C = Colors().V1;
        case 'V3'
           C = Colors().V3;
        case 'V0d'
           C = Colors().V0d;
        case 'V0v'
           C = Colors().V0v;
        case 'DI6'
           C = Colors().DI6;
        case 'MN' 
           C = Colors().MN;
        case ''
           C = [0 0 0];
    end

    ConnMat = obj.ConnMat;
    Proj = logical(sum(ConnMat(:,whr),2)); 
    ProjW = sum(ConnMat(:,whr),2); 

    L = round(obj.Position(:,2),-2);
    edges = [min(L):200:max(L)];
    yin = discretize(obj.Position(Proj,2), edges);
    [~,Wi,Ci] = grpstats(ProjW(Proj~=0), yin,["gname","mean","numel"]);

    if(mean(obj.Transmit(whr)<0))
        mul = -1;
    else
        mul = 1;
    end
    yin(isnan(yin)) = [];
    plot(edges(unique(yin)+1), Wi.*Ci,'Color',[C 0.3]);

    %bar(edges(unique(yin)+1), Wi.*Ci,'FaceColor',C,'FaceAlpha',0.3);
end