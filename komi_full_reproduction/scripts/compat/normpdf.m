function y = normpdf(x, mu, sigma)
% NORMPDF Compatibility shim when Statistics Toolbox is absent.
if nargin < 2, mu = 0; end
if nargin < 3, sigma = 1; end

y = exp(-0.5 * ((x - mu) ./ sigma).^2) ./ (sigma * sqrt(2 * pi));
end
