function tf = inROI(roi, x, y)
% INROI Compatibility shim for MATLAB without Image Processing Toolbox
% Computes whether points (x, y) lie inside a region of interest.

if isobject(roi) && isprop(roi, 'Position')
    pos = roi.Position;
elseif isstruct(roi) && isfield(roi, 'Position')
    pos = roi.Position;
elseif isnumeric(roi)
    pos = roi;
else
    error('inROI: unsupported ROI format');
end

tf = inpolygon(x, y, pos(:, 1), pos(:, 2));
end
