function y = geomean(x, dim, flag)
% GEOMEAN Geometric mean compatibility function when Statistics Toolbox is absent.
if nargin < 2 || isempty(dim)
    if isvector(x)
        dim = find(size(x) > 1, 1);
        if isempty(dim), dim = 1; end
    else
        dim = 1;
    end
end
if nargin < 3, flag = ''; end

omitnan = strcmpi(flag, 'omitnan');

is_zero = any(x == 0, dim);
log_x = log(x);

if omitnan
    valid = ~isnan(log_x) & (x > 0);
    n_valid = sum(valid, dim);
    log_x(~valid) = 0;
    sum_log = sum(log_x, dim);
    y = exp(sum_log ./ max(n_valid, 1));
    y(n_valid == 0) = NaN;
    y(is_zero) = 0;
else
    y = exp(mean(log_x, dim));
    y(is_zero) = 0;
end
end
