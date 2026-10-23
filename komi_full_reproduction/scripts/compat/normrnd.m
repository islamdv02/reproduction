function r = normrnd(mu, sigma, varargin)
    % Standalone toolbox-free implementation of normrnd
    % Located in scripts/compat/ so that source/ remains byte-for-byte identical to upstream.
    if isempty(varargin)
        if isscalar(sigma) && ~isscalar(mu)
            r = mu + sigma .* randn(size(mu));
        elseif isscalar(mu) && ~isscalar(sigma)
            r = mu + sigma .* randn(size(sigma));
        else
            r = mu + sigma .* randn(size(mu));
        end
    elseif length(varargin) == 1 && isvector(varargin{1}) && length(varargin{1}) > 1
        r = mu + sigma .* randn(varargin{1});
    else
        r = mu + sigma .* randn(varargin{:});
    end
end
