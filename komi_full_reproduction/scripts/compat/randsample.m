function y = randsample(varargin)
% RANDSAMPLE Random sample from a sequence or integer range.
%   Compat shim for base MATLAB without Statistics and Machine Learning Toolbox.
%
%   Y = RANDSAMPLE(N, K)
%   Y = RANDSAMPLE(POPULATION, K)
%   Y = RANDSAMPLE(..., REPLACEMENT)
%   Y = RANDSAMPLE(..., REPLACEMENT, W)
%   Y = RANDSAMPLE(S, ...) uses RandStream S

argIdx = 1;
s = [];
if isa(varargin{1}, 'RandStream')
    s = varargin{1};
    argIdx = 2;
end

nOrPop = varargin{argIdx};
k = varargin{argIdx + 1};

replacement = false;
if length(varargin) >= argIdx + 2 && ~isempty(varargin{argIdx + 2})
    repArg = varargin{argIdx + 2};
    if ischar(repArg) || isstring(repArg)
        replacement = strcmpi(repArg, 'true') || strcmp(repArg, '1');
    else
        replacement = logical(repArg);
    end
end

w = [];
if length(varargin) >= argIdx + 3 && ~isempty(varargin{argIdx + 3})
    w = varargin{argIdx + 3};
end

% Determine whether first argument is N or a population vector
isPopVector = false;
if isscalar(nOrPop) && isnumeric(nOrPop) && nOrPop >= 1 && floor(nOrPop) == nOrPop
    if ~isempty(w) && numel(w) == 1
        % Scalar population with 1 weight
        isPopVector = true;
        pop = nOrPop;
        N = 1;
    else
        N = nOrPop;
        pop = 1:N;
    end
else
    isPopVector = true;
    pop = nOrPop;
    N = numel(pop);
end

if k == 0
    if isPopVector
        y = pop([]);
    else
        y = zeros(0, 1);
    end
    return;
end

% Perform sampling
if isempty(w)
    % Uniform sampling
    if replacement
        if isempty(s)
            idx = randi(N, k, 1);
        else
            idx = s.randi(N, k, 1);
        end
    else
        if k > N
            error('Cannot take a sample larger than the population when replacement is false.');
        end
        if isempty(s)
            p = randperm(N);
        else
            p = s.randperm(N);
        end
        idx = p(1:k)';
    end
else
    % Weighted sampling
    w = double(w(:));
    if numel(w) ~= N
        error('Weight vector must have the same number of elements as the population.');
    end
    sumW = sum(w);
    if sumW <= 0 || any(w < 0) || isnan(sumW)
        error('Weights must be non-negative and sum to a positive number.');
    end
    prob = w / sumW;
    
    if replacement
        edges = [0; cumsum(prob)];
        edges(end) = 1; % ensure exact 1
        if isempty(s)
            u = rand(k, 1);
        else
            u = s.rand(k, 1);
        end
        [~, ~, idx] = histcounts(u, edges);
        idx(idx < 1) = 1;
        idx(idx > N) = N;
    else
        % Weighted sampling without replacement via Gumbel-max trick
        if k > N
            error('Cannot take a sample larger than the population when replacement is false.');
        end
        if isempty(s)
            u = rand(N, 1);
        else
            u = s.rand(N, 1);
        end
        g = -log(-log(u));
        scores = log(prob + eps) + g;
        [~, sortedIdx] = sort(scores, 'descend');
        idx = sortedIdx(1:k);
    end
end

if isPopVector
    % Preserve column or row vector orientation of population
    if iscolumn(pop)
        y = pop(idx);
    elseif isrow(pop)
        y = pop(idx)';
    else
        y = pop(idx);
    end
else
    y = idx;
end
end
