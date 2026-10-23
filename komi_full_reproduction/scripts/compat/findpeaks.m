function [pks, locs, w, p] = findpeaks(y, varargin)
% FINDPEAKS Compatibility shim when Signal Processing Toolbox is absent.
% Supports 'MinPeakDistance', 'MinPeakProminence', 'MinPeakHeight', and 'Threshold'.

y = y(:);
N = length(y);

if N < 3
    pks = []; locs = []; w = []; p = [];
    return;
end

% Parse options
min_dist = 1;
min_prom = 0;
min_height = -inf;
threshold = 0;

for k = 1:2:length(varargin)
    switch lower(varargin{k})
        case 'minpeakdistance'
            min_dist = varargin{k+1};
        case 'minpeakprominence'
            min_prom = varargin{k+1};
        case 'minpeakheight'
            min_height = varargin{k+1};
        case 'threshold'
            threshold = varargin{k+1};
    end
end

% 1. Find all local maxima
dy1 = y(2:N) - y(1:N-1);
% Sign changes from positive/zero to negative
is_cand = false(N, 1);
for i = 2:N-1
    if y(i) > y(i-1) && y(i) >= y(i+1)
        if (y(i) - y(i-1) >= threshold) && (y(i) - y(i+1) >= threshold)
            is_cand(i) = true;
        end
    end
end

cand_locs = find(is_cand);
if isempty(cand_locs)
    pks = []; locs = []; w = []; p = [];
    return;
end

% 2. Filter by MinPeakHeight
if ~isinf(min_height)
    cand_locs = cand_locs(y(cand_locs) >= min_height);
end

if isempty(cand_locs)
    pks = []; locs = []; w = []; p = [];
    return;
end

% 3. Calculate prominence for each candidate peak (only if needed)
prominences = zeros(length(cand_locs), 1);
if min_prom > 0 || nargout >= 4
    for k = 1:length(cand_locs)
        idx = cand_locs(k);
        val = y(idx);
        
        % Look left for highest valley before higher peak
        left_valley = val;
        for l = idx-1:-1:1
            if y(l) > val
                break;
            end
            if y(l) < left_valley
                left_valley = y(l);
            end
        end
        
        % Look right for highest valley before higher peak
        right_valley = val;
        for r = idx+1:N
            if y(r) > val
                break;
            end
            if y(r) < right_valley
                right_valley = y(r);
            end
        end
        
        base_level = max(left_valley, right_valley);
        prominences(k) = val - base_level;
    end
end

% Filter by MinPeakProminence
if min_prom > 0
    valid_prom = (prominences >= min_prom);
    cand_locs = cand_locs(valid_prom);
    prominences = prominences(valid_prom);
end

if isempty(cand_locs)
    pks = []; locs = []; w = []; p = [];
    return;
end

% 4. Enforce MinPeakDistance (keep higher peak when too close)
if min_dist > 1 && length(cand_locs) > 1
    [~, sort_idx] = sort(y(cand_locs), 'descend');
    sorted_locs = cand_locs(sort_idx);
    sorted_prom = prominences(sort_idx);
    
    keep = true(length(sorted_locs), 1);
    for k = 1:length(sorted_locs)
        if ~keep(k), continue; end
        dist_to_others = abs(sorted_locs - sorted_locs(k));
        too_close = dist_to_others < min_dist;
        too_close(k) = false; % don't eliminate self
        keep(too_close) = false;
    end
    
    final_locs = sorted_locs(keep);
    final_prom = sorted_prom(keep);
    [locs, sort_back] = sort(final_locs, 'ascend');
    p = final_prom(sort_back);
else
    locs = cand_locs;
    p = prominences;
end

pks = y(locs);
w = ones(size(pks)); % approximate width
end
