function MakeLesion(obj,ypos,varargin)
PopOfI = ones(size(obj.Types));
LayerOfI = ones(size(obj.Layers));
LatOfI = ones(size(obj.Latera));
TransOfI = ones(size(obj.Transmit));
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
        end
    end

    Whr = PopOfI&LayerOfI&LatOfI&TransOfI;
    source = obj.Position(:,2) < ypos & Whr;
    target = obj.Position(:,2) > ypos & Whr;
    obj.Lesion = obj.Lesion | (((source&target')|(target&source')) & (obj.ConnMat ~= 0));
    obj.ConnMat(obj.Lesion)= 0;
end