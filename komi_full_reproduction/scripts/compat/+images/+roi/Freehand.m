classdef Freehand < handle
    properties
        Position
        Waypoints
        Type
        Label
        Color
        LineWidth
        Selected
        InteractionsAllowed
        Parent
    end
    methods
        function obj = Freehand(varargin)
            if nargin > 0
                obj.Position = varargin{1};
            end
        end
        function tf = inROI(obj, x, y)
            if isempty(obj.Position)
                tf = false(size(x));
            else
                tf = inpolygon(x, y, obj.Position(:, 1), obj.Position(:, 2));
            end
        end
    end
    methods (Static)
        function obj = loadobj(s)
            obj = images.roi.Freehand();
            if isstruct(s)
                if isfield(s, 'PositionInternal')
                    obj.Position = s.PositionInternal;
                end
                if isfield(s, 'WaypointsInternal')
                    obj.Waypoints = s.WaypointsInternal;
                end
                fn = fieldnames(s);
                for k = 1:length(fn)
                    try obj.(fn{k}) = s.(fn{k}); catch, end
                end
            end
        end
    end
end
