function r = binornd(n, p, varargin)
% BINORND Compatibility shim when Statistics Toolbox is absent.
if nargin > 2
    if length(varargin) == 1 && isvector(varargin{1})
        sz = varargin{1};
    else
        sz = [varargin{:}];
    end
else
    sz = size(p);
end

if isscalar(n) && n == 1
    r = double(rand(sz) < p);
else
    if isscalar(n)
        r = zeros(sz);
        for i = 1:n
            r = r + double(rand(sz) < p);
        end
    else
        % Element-wise
        r = zeros(sz);
        for i = 1:max(n(:))
            mask = (n >= i);
            r(mask) = r(mask) + double(rand(sum(mask(:)), 1) < p(mask));
        end
    end
end
end
