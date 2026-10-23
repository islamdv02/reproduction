function varargout = grpstats(X, group, whichstats, varargin)
    % Standalone implementation of grpstats for basic groupings
    % Located in scripts/compat/ so that source/ remains byte-for-byte identical to upstream.
    valid = ~isnan(group);
    X = X(valid);
    group = group(valid);
    
    unique_grps = unique(group);
    n_grps = length(unique_grps);
    
    means = zeros(n_grps, 1);
    numels = zeros(n_grps, 1);
    gnames = cell(n_grps, 1);
    
    for k = 1:n_grps
        g = unique_grps(k);
        idx = (group == g);
        means(k) = mean(X(idx));
        numels(k) = sum(idx);
        gnames{k} = num2str(g);
    end
    
    % Return requested statistics
    if nargin >= 3 && isstring(whichstats)
        whichstats = cellstr(whichstats);
    end
    
    if nargin < 3 || isempty(whichstats)
        varargout{1} = means;
    else
        for i = 1:min(nargout, length(whichstats))
            stat_name = lower(whichstats{i});
            switch stat_name
                case 'gname'
                    varargout{i} = gnames;
                case 'mean'
                    varargout{i} = means;
                case 'numel'
                    varargout{i} = numels;
                otherwise
                    varargout{i} = means;
            end
        end
    end
end
