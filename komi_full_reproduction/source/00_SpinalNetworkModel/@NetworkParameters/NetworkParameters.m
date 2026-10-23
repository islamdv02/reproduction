classdef NetworkParameters <  handle & matlab.mixin.Copyable
    properties (Access = private)
        Celltypes = Celltype.empty;
    end

    properties (SetAccess = public)
        Types = categorical();
        BiasRC = categorical(); 
        BiasDV = categorical();
        BiasML = categorical();
        BiasMN = categorical();
        BiasContraIpsi = categorical();
        BiasLayer = categorical();
        BiasSegment = categorical();
        BiasPop = [];
        DelaysPop = [];
        LengthScales = [];
        PresSyns = [];
        SynStrengths = [];
        Gains = [];
        F_max = [];
        Thresholds = [];
    end

    properties (Access=private)
        listeners = event.listener.empty
    end
    
    methods 
        function AddCelltype(obj,Type,BiasRC,BiasDV,BiasML,BiasMN,BiasContraIpsi,BiasLayer,BiasSeg,LengthScale,varargin)
            gain = 1;
            f_max = 50;
            thresh = 5;
            synst = 1;
            presyn =  [];
            for ii = 1:2:length(varargin)
                switch varargin{ii}
                    case 'Gain'
                        gain = varargin{ii+1};
                    case 'Threshold'
                        thresh = varargin{ii+1};
                    case 'f_max'
                        f_max = varargin{ii+1};
                    case 'SynStrength'
                        synst = varargin{ii+1};
                    case 'PreSyn'
                        presyn = varargin{ii+1};
                end
            end
            obj.Celltypes(length(obj.Celltypes)+1) = Celltype(Type,BiasRC,BiasDV,BiasML,BiasMN,BiasContraIpsi,BiasLayer,BiasSeg,LengthScale,gain,thresh,f_max,synst,presyn);
            obj.listeners(length(obj.listeners)+1) = addlistener(obj.Celltypes(end),'StateChanged',@obj.HandleStatChanged); 
            obj.UpdateFields();
        end
        function RemoveCelltype(obj,Type)
            ix = [obj.Celltypes.Type] == categorical(string(Type));
            obj.Celltypes(ix) = [];
            delete(obj.listeners(ix));
            obj.UpdateFields();
        end 
        function SetCellBiasPop(obj,source,target,value)

            if strcmpi(source,'All')
                for T = obj.Types
                    si = [obj.Types] == T;
                    obj.Celltypes(si).SetBiasPop(target,value);
                end
            else
                si = [obj.Types] == categorical(string(source));
                obj.Celltypes(si).SetBiasPop(target,value);
            end
        end
        function SetCellDelaysPop(obj,source,target,value)
            si = [obj.Types] == categorical(string(source));
            obj.Celltypes(si).SetDelaysPop(target,value);
        end
    end
    methods (Access= private)
        function HandleStatChanged(obj,src,eventData)
            obj.UpdateFields()
        end
        function UpdateFields(obj)
            obj.Types = [obj.Celltypes.Type];
            obj.BiasRC = [obj.Celltypes.BiasRC];
            obj.BiasDV = [obj.Celltypes.BiasDV];
            obj.BiasML = [obj.Celltypes.BiasML];
            obj.BiasMN = [obj.Celltypes.BiasMN];
            obj.BiasPop = ones(length(obj.Types),length(obj.Types));
            for pop = 1:length(obj.Types) 
                cellfun(@(x) UpdateBiasPop(obj,obj.Types(pop),x{1},x{2}),obj.Celltypes(pop).BiasPop);
            end
            obj.DelaysPop = zeros(length(obj.Types),length(obj.Types));
            for pop = 1:length(obj.Types) 
                cellfun(@(x) UpdateDelaysPop(obj,obj.Types(pop),x{1},x{2}),obj.Celltypes(pop).DelaysPop);
            end
            obj.BiasContraIpsi = [obj.Celltypes.BiasContraIpsi];   
            obj.BiasLayer = {obj.Celltypes.BiasLayer};
            obj.BiasSegment = {obj.Celltypes.BiasSegment };
            obj.LengthScales = [obj.Celltypes.LengthScale];
            obj.SynStrengths = [obj.Celltypes.SynStrength];
            obj.Gains = [obj.Celltypes.Gain];
            obj.F_max = [obj.Celltypes.F_max];
            obj.Thresholds = [obj.Celltypes.Threshold];
        end 
        function UpdateBiasPop(obj,source,target,value)
            if target == categorical("All")
                ti = true(size(obj.Types));
            else
                ti = [obj.Types] == categorical(string(target));
            end
            si = [obj.Types] == categorical(string(source));
            obj.BiasPop(ti'&si) = value;
        end
        function UpdateDelaysPop(obj,source,target,value)
            if target == categorical("All")
                ti = true(size(obj.Types));
            else
                ti = [obj.Types] == categorical(string(target));
            end
            si = [obj.Types] == categorical(string(source));
            obj.DelaysPop(ti'&si) = value;
        end
    end
end