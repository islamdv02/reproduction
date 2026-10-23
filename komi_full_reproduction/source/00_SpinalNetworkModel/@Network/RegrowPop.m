function RegrowPop(obj,pop,varargin)
Latera = ones(size(obj.Latera));
    for jj = 1:2:length(varargin)
        switch varargin{jj}
            case 'Latera'
                Latera = obj.Latera == varargin{jj+1};
        end
    end
    restore = obj.Lesion & (Latera') & (obj.Types == pop)';
    obj.ConnMat(restore) = mean(nonzeros(obj.ConnMat(:,obj.Types == pop)),'all');
    obj.Lesion(restore) = 0; 
    %obj.ConnMat = BalanceConnectivity(obj.ConnMat);
end