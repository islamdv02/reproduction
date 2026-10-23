function y = range(x, dim)
% RANGE Sample range (compat shim for base MATLAB without Stats Toolbox).
%   Y = RANGE(X) returns the difference between the maximum and the minimum
%   values of X.
%   Y = RANGE(X, DIM) operates along dimension DIM.

if nargin < 2
    if isvector(x)
        y = max(x) - min(x);
    else
        y = max(x, [], 1) - min(x, [], 1);
    end
else
    y = max(x, [], dim) - min(x, [], dim);
end
end
