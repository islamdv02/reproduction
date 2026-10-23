classdef Celltype <  handle & matlab.mixin.Copyable
    properties(Constant)
        %% Ventral Interneurons
        V1 = categorical("V1")
        V1r = categorical("V1r")
        V1_Ia = categorical("V1-Ia")
        V2a_1 = categorical("V2a-1")
        V2a_2 = categorical("V2a-2")
        V0d = categorical("V0d")
        V0v = categorical("V0v")
        V2b = categorical("V2b")
        V2b_Ia = categorical("V2b-Ia")
        MN = categorical("MN")
        V3 = categorical("V3")
        DI6 = categorical("DI6")
        Lhx9 = categorical("Lhx9Syt2")
        %% Sensory Neurons
        NF1 = categorical("NF1")
        NF2 = categorical("NF2")
        NF3 = categorical("NF3")
        NF4 = categorical("NF4")
        NF5 = categorical("NF5")
        NP1 = categorical("NP1")
        NP2 = categorical("NP2")
        NP3 = categorical("NP3")
        PEP1 = categorical("PEP1")
        PEP2 = categorical("PEP2")
        TH = categorical("TH")
        %% Dorsal Interneurons
        Cpne4 = categorical("CckCpne4")
        Cpne8 = categorical("CckCpne8")
        CckRorb = categorical("CckRorb")
        CckTrh = categorical("CckTrh")
        Cdh3 = categorical("Cdh3")
        Crabp1 = categorical("Crabp1")
        CSF_N = categorical("CSF-N")
        Ecel1 = categorical("Ecel1")
        GalPdyn = categorical("GalPdyn")
        Grp = categorical("Grp")
        Grpr = categorical("Grpr")
        Lhx1 = categorical("Lhx1Nxph1")
        Cbln2 = categorical("MafCbln2")
        MafRora = categorical("MafRora")
        Man1a = categorical("Man1a")
        Nmu = categorical("Nmu")
        Npy = categorical("Npy")
        Npy1r = categorical("Npy1r")
        Nts = categorical("Nts")
        Ptf1a = categorical("Ptf1a")
        ReIn = categorical("ReIn")
        RoraAdarb2 = categorical("RoraAdarb2")
        Rora_I = categorical("Rora-I")
        Rorb = categorical("Rorb")
        Rorb_I = categorical("Rorb-I")
        Rxfp2 = categorical("Rxfp2")
        Tac1Sox5 = categorical("Tac1Sox5")
        Tac1Gpr101 = categorical("Tac1Gpr101")
        Tac2 = categorical("Tac2")
    end

    properties (SetObservable)
        Type 
        BiasRC
        BiasDV
        BiasML
        BiasMN
        BiasPop = [];
        DelaysPop =[];
        BiasContraIpsi
        BiasLayer
        BiasSegment
        LengthScale
        PreSyn
        SynStrength = 1;
        Gain = 0.7
        F_max = 60
        Threshold = 40
    end
    methods 
        function obj = Celltype(Type,BiasRC,BiasDV,BiasML,BiasMN,BiasContraIpsi,BiasLayer,BiasSeg,LengthScale,Gain,Threshold,F_max,SynSt,PreSyn)
            obj.Type = categorical(string(Type));
            obj.BiasRC = categorical(string(BiasRC));
            obj.BiasDV = categorical(string(BiasDV));
            obj.BiasML = categorical(string(BiasML));
            obj.BiasMN = categorical(string(BiasMN)); 
            if(isempty(obj.BiasPop))
                BiasPop = {{categorical("All"),1}};
            end
            obj.BiasPop = cellfun(@(x) {categorical(string(x{1})),x{2}},BiasPop,'UniformOutput',false);
            if(isempty(obj.DelaysPop))
                DelaysPop = {{categorical("All"),0}};
            end
            obj.DelaysPop = cellfun(@(x) {categorical(string(x{1})),x{2}},DelaysPop,'UniformOutput',false);
            obj.BiasContraIpsi = categorical(string(BiasContraIpsi));
            obj.BiasLayer = categorical(string(BiasLayer));
            obj.BiasSegment = categorical(string(BiasSeg));
            obj.LengthScale = double(LengthScale);
            obj.PreSyn = categorical(string(PreSyn));
            obj.SynStrength = double(SynSt);
            obj.Gain = double(Gain);
            obj.F_max = double(F_max);
            obj.Threshold = double(Threshold);
            obj.AttachListener();
        end
        function obj = SetBiasPop(obj,target,value)
            ix = cellfun(@(x)categorical(x) == categorical(string(target)),[obj.BiasPop{:}]); 
            if(any(ix))
                ci=(find(ix)+1)/2;
                obj.BiasPop{ci}{2} = value;
            else
                obj.BiasPop = cat(2,obj.BiasPop,{{categorical(string(target)),value}});
            end
        end
        function obj = SetDelaysPop(obj,target,value)
            ix = cellfun(@(x)categorical(x) == categorical(string(target)),[obj.DelaysPop{:}]); 
            if(any(ix))
                ci=(find(ix)+1)/2;
                obj.DelaysPop{ci}{2} = value;
            else
                obj.DelaysPop = cat(2,obj.DelaysPop,{{categorical(string(target)),value}});
            end
        end
    end
    methods (Access = private)
        function AttachListener(obj)
            addlistener(obj,'Type','PostSet',@Celltype.handlePropEvents);
            addlistener(obj,'BiasRC','PostSet',@Celltype.handlePropEvents);
            addlistener(obj,'BiasDV','PostSet',@Celltype.handlePropEvents);
            addlistener(obj,'BiasML','PostSet',@Celltype.handlePropEvents);
            addlistener(obj,'BiasContraIpsi','PostSet',@Celltype.handlePropEvents);
            addlistener(obj,'BiasLayer','PostSet',@Celltype.handlePropEvents);
            addlistener(obj,'BiasSegment','PostSet',@Celltype.handlePropEvents);
            addlistener(obj,'BiasPop','PostSet',@Celltype.handlePropEvents);
            addlistener(obj,'DelaysPop','PostSet',@Celltype.handlePropEvents);
            addlistener(obj,'LengthScale','PostSet',@Celltype.handlePropEvents);
            addlistener(obj,'PreSyn','PostSet',@Celltype.handlePropEvents);
            addlistener(obj,'SynStrength','PostSet',@Celltype.handlePropEvents);
            addlistener(obj,'Gain','PostSet',@Celltype.handlePropEvents);
            addlistener(obj,'Threshold','PostSet',@Celltype.handlePropEvents);
            addlistener(obj,'F_max','PostSet',@Celltype.handlePropEvents);
        end
    end
    methods (Static, Access= private)
        function handlePropEvents(metaProp,eventData)
            notify(eventData.AffectedObject,'StateChanged');
        end
    end
    events
        StateChanged 
    end 
end