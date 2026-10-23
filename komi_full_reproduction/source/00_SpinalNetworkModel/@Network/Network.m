classdef Network < handle & matlab.mixin.Copyable
    properties
        ConnMat
        Sparsity 
        Delays
        Position 
        Types 
        Latera
        Transmit
        Lesion
        Layers  
        Descending
        Segment
        MnID
        FlexExtID 
        Rates
        Voltage
        EstimatedRates
        Spikes
        PC
        Phase 
        NullSpace
        EigenValues
        EigenModes
        Parameters
    end

    properties (Hidden)
        isSymetric
        Geometry
        Genetics 
        Colors
    end

    methods (Access = public)
        function obj = Network(Length,Density,Symmetry,Parameters,varargin)
            obj.Parameters = Parameters;
            obj.Genetics = SpinalCordGenetics.GetMouseGenetics(Symmetry);
            obj.Geometry = SpinalCordGeometry.GetMouseGeometry(Length,Density,Symmetry); 
            obj.InstantiateNetwork(obj.Geometry,obj.Genetics,obj.Parameters,varargin{:});
            obj.isSymetric = Symmetry;
        end        
    end

    methods (Access = public)
        Simulate(obj,t_steps,varargin)
    end

    methods(Access=public)
        InstantiateNetwork(obj,Geometry,Parameters,varargin)
        PlotRates(obj,varargin)
        PlotRaster(obj,varargin)
        PolarPlotTargets(obj,UoI,varargin)
        PolarPlotLogFC(obj,Gene,varargin)
        PlotEMG(obj,varargin)
        PlotNeurogram(obj,varargin)
        PlotGeneLocation(obj,Genes,varargin)
        AnimatedPlotRates(obj,varargin)
        ComputeEigenModesandNullSpace(obj,varargin)
        MakeLesion(obj,ypos,varargin)
        RegrowPop(obj,pop,varargin)
        UoI = GetNeuronsInDiffGeneExpSpatial(obj,Gene,varargin)
        UoI = GetNeuronsInDiffGeneExpSingleCell(obj,Gene,varargin)
        GoI = GetGenesDiffExpSingleCell(obj,Pops,varargin)
    end

    methods(Access=public)
        function  ComputePhase(obj,varargin)
           
            UoI = true(size(obj.ConnMat,1),1);
            for ii = 1:2:length(varargin)
                switch varargin{ii}
                    case 'UoI'
                       UoI = varargin{ii+1};
                end
            end
            FiringMat = obj.Rates(:,UoI);
            [~,s,~] = pca(FiringMat);
            whole = s(:,1); 
            scores = [];
            corrs = [];
            for n = 1:size(obj.Rates,2)
                [C,L] = xcorr(whole,obj.Rates(:,n));
                [maxVal,loc] = max(C);
                scores = [scores L(loc)];
                corrs = [corrs maxVal];
            end
            
            [autocor,~] = xcorr(whole);
            [~,lcsh] = findpeaks(autocor);
            short = mean(diff(lcsh));
           
            scores =rem((scores.*2*pi)./short,2*pi);
            obj.Phase = mod(scores'+2*pi,2*pi);
        end
        function  ComputePC(obj,varargin)
            UoI = true(size(obj.ConnMat,1),1);
            Est = 0;
            Source = true(1,size(obj.Rates,1));
            for ii = 1:2:length(varargin)
                switch varargin{ii}
                    case 'UoI'
                       UoI = varargin{ii+1};
                    case 'Estimated'
                       Est = varargin{ii+1};
                    case 'Source'
                        Source = varargin{ii+1};
                end
            end
            if(Est)
                FiringMat = obj.EstimatedRates;
            else
                FiringMat = obj.Rates;
            end
            FM = FiringMat;
            [c,s,~] = pca(FM(Source,UoI));
            obj.PC = FiringMat(:,UoI)*c;
        end
        function  ComputeEstimatedRates(obj,varargin)
            if(isempty(obj.Spikes))
                obj.ComputeSpikes;
            end
            obj.EstimatedRates = GetGaussianFiring(obj.Spikes,50,1000); 
        end
        function  ComputeSpikes(obj,varargin)
            UoI = true(size(obj.ConnMat,1),1);
            for ii = 1:2:length(varargin)
                switch varargin{ii}
                    case 'UoI'
                       UoI = varargin{ii+1};
                end
            end
            RI =  obj.Rates(1:end,UoI);
            RIsp = ((RI-min(RI,[],1)));
            RIsp = RIsp./(max(RIsp,[],1));
            Poiss = poissrnd(RIsp/75,size(RIsp));
            obj.Spikes = logical(Poiss);
        end

    end
end