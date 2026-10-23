function obj = InstantiateNetwork(obj,Geometry,Genetics,Parameters,varargin)
    verbose = 1;
    var = 0.1;
    RC = 0;
    SP = 0;
    Bal = 1;
    resc = 1;
    projwidth = 500;
    if(~isempty(varargin))
        for ii = 1:2:length(varargin)
            switch varargin{ii}
                case 'Verbose'
                    verbose = varargin{ii+1};
                case 'RandomComp'
                    RC = varargin{ii+1};
                case 'Sparsify'
                    SP = 1;
                    sparsity = varargin{ii+1};
                case 'Balance'
                    Bal = varargin{ii+1};
                case 'Rescale'
                    resc = varargin{ii+1};
                case 'ProjWidth'
                    projwidth = varargin{ii+1};
            end 
        end
    end

%% Define Geometry and parameters for instantiation of the model 
    PopModel = false(size(Geometry,1),1);
    for ii = 1:length(Parameters.Types)
        PopModel = PopModel | (Geometry.Type == Parameters.Types(ii));
    end 
    SC = Geometry(PopModel,:);
    BiasPop = ComputePopulationProjectionBias(SC,Parameters);
    DelaysPop = ComputePopulationDelays(SC,Parameters);
%% Generate Bias Map 
    PosX = SC.Position(:,2)';
    PosY = SC.Position(:,1)';
    PosZ = SC.Position(:,3)';

    E = (SC.Transmit > 0); % Excitatory Neurons
    I = (SC.Transmit < 0); % Inhibitory Neurons 

    CellIndex = cellfun(@(x,y) x.*(SC.Type == y),{1:length(Parameters.Types)},{Parameters.Types},'UniformOutput',false);
    CellIndex = sum(CellIndex{1,1},2); % List of integer for indexation

    %% Compute pairwise distances in all 3 dimensions
    DistRC = -bsxfun(@minus,PosX,PosX');   
    DistML = -bsxfun(@minus,abs(PosY),abs(PosY)');
    DistDV = -bsxfun(@minus,PosZ,PosZ');
    DistCI = SC.Latera*SC.Latera';
    %% Initialize Bias Matrices
    BiasRC = nan(size(DistRC));
    BiasML = nan(size(DistML));
    BiasDV = nan(size(DistDV));
    BiasCI = ones(size(DistCI));
    BiasLay = ones(size(DistCI));
    BiasSeg = ones(size(DistCI));
    BiasMn = ones(size(DistCI));
    BiasModule = ones(size(DistCI));

    bRC = unique(Parameters.BiasRC);
    bML = unique(Parameters.BiasML);
    bDV = unique(Parameters.BiasDV);
    bCI = unique(Parameters.BiasContraIpsi);
    bLay = Parameters.BiasLayer;
    bSeg = Parameters.BiasSegment;
    bMn = Parameters.BiasMN;
%% Compute Rostro-Caudal Bias Matrix 
    for brc = bRC
        ioi = ismember(SC.Type,Parameters.Types(Parameters.BiasRC == brc))';
        switch brc
            case 'cau'
                divider = repmat(Parameters.LengthScales(CellIndex),[size(DistRC,1),1]);
                divider = divider + repmat(normrnd(0,mean(divider,1)/10,[1 size(divider,1)]),[size(DistRC,1),1]);
                BiasRC(DistRC>0 & ioi) = (DistRC(DistRC>0 & ioi)-divider(DistRC>0 & ioi))/projwidth;
                BiasRC(DistRC<0 & ioi) = (DistRC(DistRC<0 & ioi)-divider(DistRC<0 & ioi))/projwidth;
            case 'ro'
                divider = repmat(Parameters.LengthScales(CellIndex),[size(DistRC,1),1]);
                divider = divider + repmat(normrnd(0,mean(divider,1)/10,[1 size(divider,1)]),[size(DistRC,1),1]);
                BiasRC(DistRC>0 & ioi) = (DistRC(DistRC>0 & ioi)+divider(DistRC>0 & ioi))/projwidth;
                BiasRC(DistRC<0 & ioi) = (DistRC(DistRC<0 & ioi)+divider(DistRC<0 & ioi))/projwidth;
            case 'bi'
                divider = Parameters.LengthScales(CellIndex(ioi));
                divider = divider + normrnd(0,divider/10,size(divider));
                BiasRC(:,ioi) = (abs(DistRC(:,ioi))-divider)/projwidth;
            case 'loc'
                divider = repmat(Parameters.LengthScales(CellIndex),[size(DistRC,1),1]);
                divider = divider + repmat(normrnd(0,mean(divider,1)/10,[1 size(divider,1)]),[size(DistRC,1),1]);
                BiasRC(DistRC>0 & ioi) = (DistRC(DistRC>0 & ioi)./divider(DistRC>0 & ioi));
                BiasRC(DistRC<0 & ioi) = (DistRC(DistRC<0 & ioi)./divider(DistRC<0 & ioi));
        end
        BiasRC(DistRC==0 & ioi) = 0;
    end
 %% Compute Medio-Lateral Bias Matrix 
    for bml = bML
        ioi = ismember(SC.Type,Parameters.Types(Parameters.BiasML == bml))';
        switch bml
            case 'lat'
                divider = repmat(Parameters.LengthScales(CellIndex),[size(DistML,1),1]);
                BiasML(DistML>0 & ioi) = abs(DistML(DistML>0 & ioi))./(2*projwidth);
                BiasML(DistML<0 & ioi) = abs(DistML(DistML<0 & ioi))./(projwidth/5);
            case 'med'
                divider = repmat(Parameters.LengthScales(CellIndex),[size(DistML,1),1]);
                BiasML(DistML>0 & ioi) = abs(DistML(DistML>0 & ioi))./(projwidth/5);
                BiasML(DistML<0 & ioi) = abs(DistML(DistML<0 & ioi))./(2*projwidth);
            case 'loc'
                BiasML(:,ioi) = abs(DistML(:,ioi))./(projwidth/5);
        end
        BiasML(DistML==0 & ioi) = 0;
    end
%% Compute Dorso-Ventral Bias Matrix 
    for bdv = bDV
        ioi = ismember(SC.Type,Parameters.Types(Parameters.BiasDV == bdv))';
        switch bdv
            case 'dor'
                divider = repmat(Parameters.LengthScales(CellIndex),[size(DistDV,1),1]);
                BiasDV(DistDV>0 & ioi) = abs(DistDV(DistDV>0 & ioi))./(2*projwidth);
                BiasDV(DistDV<0 & ioi) = abs(DistDV(DistDV<0 & ioi))./(projwidth/5);
            case 'ven'
                divider = repmat(Parameters.LengthScales(CellIndex),[size(DistDV,1),1]);
                BiasDV(DistDV>0 & ioi) = abs(DistDV(DistDV>0 & ioi))./(projwidth/5);
                BiasDV(DistDV<0 & ioi) = abs(DistDV(DistDV<0 & ioi))./(2*projwidth);
            case 'loc'
                BiasDV(:,ioi) = abs(DistDV(:,ioi))./(projwidth/5);
        end
        BiasDV(DistDV==0 & ioi) = 0;
    end
%% Compute Contra-Ipsi Bias Matrix 
    for bci = bCI
        ioi = ismember(SC.Type,Parameters.Types(Parameters.BiasContraIpsi == bci))';
        switch bci
            case 'contra'
                BiasCI(DistCI<0 & ioi) = 1;
                BiasCI(DistCI>0 & ioi) = 0;
            case 'ipsi'
                BiasCI(DistCI>0 & ioi) = 1;
                BiasCI(DistCI<0 & ioi) = 0;
            case 'bi'
                BiasCI(DistCI>0 & ioi) = 0.2;
                BiasCI(DistCI<0 & ioi) = 1;
        end
    end
%% Compute Layer Bias Matrix 

    for bl = bLay
        if(~isundefined(bl{1}))
            ibl = cellfun(@(x) isempty(setxor(bl{1},x)),Parameters.BiasLayer);
            ioi = ismember(SC.Type,Parameters.Types(ibl))';
            BiasLay((~sum(contains(string(SC.Layers),string(bl{1})),2))&ioi) = 0.05;
        end
    end
%% Compute Segment Bias Matrix 

    for bS = bSeg
        if(~isundefined(bS{1}))
            ibS = cellfun(@(x) isempty(setxor(bS{1},x)),Parameters.BiasSegment);
            ioi = ismember(SC.Type,Parameters.Types(ibS))';
            BiasSeg((~sum(contains(string(SC.Layers(:,4)),string(bS{1})),2))&ioi) = 0.5;
        end
    end
%% Compute Motoneurons Bias Matrix 
   for bmn = bMn
        if(~isundefined(bmn))
            imn = ismember(Parameters.BiasMN,bmn);
            ioi = ismember(SC.Type,Parameters.Types(imn))';
            if(contains(string(bmn),'only'))
                bmnn = erase(string(bmn),'only');
                BiasMn(((~ismember(SC.FlexExtID,bmnn))&ismember(SC.Type,'MN'))&ioi) = 0.05;
            else
                BiasMn(((~(ismember(SC.FlexExtID,bmn)|ismember(SC.FlexExtID,'Bi')))&ismember(SC.Type,'MN'))&ioi) = 0.3;
            end
        end
   end
%% !!! DEVELOPMENT NOT FINISHED HERE
   for bmn = bMn
        if(~isundefined(bmn))
            imn = ismember(Parameters.BiasMN,bmn);
            ioi = ismember(SC.Type,Parameters.Types(imn))';
            BiasModule(~(ioi')&ioi) = 0.75;
        end
    end
%% Compute Synaptic probability matrix by combining all bias matrices
    Prob = zeros(size(BiasRC));
    if(all(isnan(BiasML(:))) && all(isnan(BiasDV(:))) && all(isnan(BiasRC(:))))
         Prob(:) = BiasCI(:).*BiasPop(:).*BiasLay(:).*BiasMn(:);
    else
         Prob(:) = geomean([normpdf(BiasML(:),0,1)./normpdf(0,0,1),normpdf(BiasDV(:),0,1)./normpdf(0,0,1),normpdf(BiasRC(:),0,1)./normpdf(0,0,1)],2,'omitnan').*BiasCI(:).*BiasPop(:).*BiasLay(:).*BiasSeg(:).*BiasMn(:);
    end
    Prob(isnan(Prob)) = 0;
%% Add Random Component to connectivity if specified 
    if SP
        Spar = zeros(size(Prob));
        ixs = randsample(1:1:numel(Spar),round(numel(Spar)*sparsity),0);
        Prob(ixs) = 0;
    end   
    %% Compute Connection Probability and sparsify
    Sparsifier = binornd(1,Prob); % Sparsify based on binomial proba
    Connectivity = normrnd(1,var,size(Prob)); % Attribute random strength with mean 1
    Connectivity(:,E) = abs(Connectivity(:,E)).*Parameters.SynStrengths(CellIndex(E)); % Bias Mean 
    Connectivity(:,I) = -(Connectivity(:,I)).*Parameters.SynStrengths(CellIndex(I));
    
    Connectivity = Connectivity.*Sparsifier;
    Connectivity = Connectivity - diag(diag(Connectivity)); % Remove self synapse
    Connectivity = UnifySensoryInputProjection(Connectivity,SC);
    Connectivity = UnifyMNConnectivity(Connectivity,SC);

    if(Bal)
        Connectivity(SC.Latera>0,:) = BalanceConnectivity(Connectivity(SC.Latera>0,:));
        Connectivity(SC.Latera<0,:) = BalanceConnectivity(Connectivity(SC.Latera<0,:));
    end
    if(resc)
        Connectivity(SC.Latera>0,:) = RescaleConnectivity(Connectivity(SC.Latera>0,:));
        Connectivity(SC.Latera<0,:) = RescaleConnectivity(Connectivity(SC.Latera<0,:));
    end

    if RC
        RandComp = zeros(size(Connectivity));
        ixs = randsample(1:1:numel(RandComp),round(numel(RandComp)/2),0);
        RandComp(ixs) = normrnd(0,std(abs(Connectivity(Connectivity~=0)),[],"all")/1,[1 numel(ixs)]);
        Connectivity(Connectivity~=0) = Connectivity(Connectivity~=0) + RandComp(Connectivity~=0);
    end     

    obj.Sparsity = nnz(~Connectivity)/numel(Connectivity);
    obj.ConnMat = Connectivity;
    obj.Delays = DelaysPop;
    obj.Position = SC.Position;
    obj.Types = SC.Type;
    obj.Latera = SC.Latera;
    obj.Transmit = SC.Transmit;
    obj.Layers = categorical(SC.Layers(:,1));
    obj.Segment = categorical(SC.Layers(:,4));
    obj.MnID = SC.MnID;
    obj.FlexExtID = SC.FlexExtID;
    obj.Lesion = zeros(size(obj.ConnMat));
    obj.Descending = SC.Descending;
    obj.ComputeEigenModesandNullSpace('Verbose',verbose)
end
%%
function Connectivity = UnifySensoryInputProjection(Connectivity,SC)
    sens = contains(string(SC.Type),'NF') | contains(string(SC.Type),'NP') | contains(string(SC.Type),'PEP') | contains(string(SC.Type),'TH');
    whr = logical(Connectivity);
    intype = repmat(SC.MnID',[length(SC.MnID) 1]);    
    intype(~whr) = '<undefined>';
    for jj = find(sens)'
        temp_out = intype(jj,:);
        temp_out(isundefined(temp_out)) = [];
        temp_out = unique(temp_out);
        if(~isempty(temp_out))
            mde = randsample(temp_out,1,true,ones(1,length(temp_out))/length(temp_out));
            notMN = (~(SC.MnID == mde))&(SC.Type=='MN');
            Connectivity(jj,notMN) = 0;
            Connectivity(notMN,jj) = 0;
        end
    end
end

%%
function Connectivity = UnifyMNConnectivity(Connectivity,SC)
    Mn = contains(string(SC.Type),'MN');
    whr = logical(Connectivity);
    intype = repmat(SC.MnID',[length(SC.MnID) 1]);    
    intype(~whr) = '<undefined>';
    for jj = find(Mn)'
        temp_out = intype(jj,:);
        temp_out(isundefined(temp_out)) = [];
        temp_out = unique(temp_out);
        if(~isempty(temp_out))
            mde = SC.MnID(jj);
            notMN = (~(SC.MnID == mde))&(SC.Type=='MN');
            Connectivity(jj,notMN) = 0;
            Connectivity(notMN,jj) = 0;
        end
    end
end

%%


