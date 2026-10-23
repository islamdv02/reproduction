function r = poissrnd(lambda, varargin)
% POISSRND Compatibility shim when Statistics Toolbox is absent.
% Generates Poisson random numbers using Knuth's algorithm.

if nargin > 1
    if length(varargin) == 1 && isvector(varargin{1})
        sz = varargin{1};
    else
        sz = [varargin{:}];
    end
    if isscalar(lambda)
        lambda = repmat(lambda, sz);
    end
else
    sz = size(lambda);
end

r = zeros(sz);
lambda_flat = lambda(:);

% For small lambda (<= 30), Knuth's algorithm (vectorized)
small_mask = (lambda_flat <= 30);
if any(small_mask)
    lam = lambda_flat(small_mask);
    L = exp(-lam);
    k = zeros(size(lam));
    p = ones(size(lam));
    active = true(size(lam));
    while any(active)
        p(active) = p(active) .* rand(sum(active), 1);
        k(active) = k(active) + 1;
        active = active & (p > L);
    end
    r(small_mask) = k - 1;
end

% For large lambda (> 30), Gaussian approximation with continuity correction
large_mask = ~small_mask;
if any(large_mask)
    lam_lg = lambda_flat(large_mask);
    r(large_mask) = max(0, round(lam_lg + sqrt(lam_lg) .* randn(size(lam_lg))));
end

r = reshape(r, sz);
end
