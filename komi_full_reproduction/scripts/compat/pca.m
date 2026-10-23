function [coeff, score, latent, tsquared, explained, mu] = pca(X, varargin)
% PCA compatibility shim for MATLAB when Statistics Toolbox is absent.
% Calculates principal component coefficients, scores, and latent variances.

if isempty(X)
    coeff = []; score = []; latent = []; tsquared = []; explained = []; mu = [];
    return;
end

mu = mean(X, 1);
X0 = bsxfun(@minus, X, mu);
n = size(X0, 1);
p = size(X0, 2);

if n >= p
    % When n >= p, computing via covariance matrix (BLAS GEMM + symmetric eig)
    % is much faster and more memory efficient than full SVD
    C = (X0' * X0) ./ max(1, n - 1);
    C = (C + C') / 2; % ensure strict symmetry
    [V, D] = eig(C);
    [d, idx] = sort(diag(D), 'descend');
    coeff = V(:, idx);
    latent = max(0, d);
    score = X0 * coeff;
else
    [U, S, V] = svd(X0, 'econ');
    coeff = V;
    score = U * S;
    latent = (diag(S).^2) ./ max(1, n - 1);
end

if nargout > 4
    tot = sum(latent);
    if tot > 0
        explained = 100 * latent / tot;
    else
        explained = zeros(size(latent));
    end
end

if nargout > 3
    valid = latent > 1e-12;
    tsquared = sum((score(:, valid) ./ sqrt(latent(valid)')).^2, 2);
end
end
