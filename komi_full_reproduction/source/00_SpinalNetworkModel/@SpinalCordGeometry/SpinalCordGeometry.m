classdef SpinalCordGeometry
    
    properties(Constant)
        Dorsal = {'1Sp','2SpO','2SpL','3Sp','4Sp','5SpM','5SpL'}
        Intermediate = {'6SpM','6SpL','10Sp','D'}
        Ventral =  {'7Sp','8Sp'}
        MN = {'Q9','Ad9','CFl9'}
        DRG = {'DRG'}
    end

    methods (Static)
        function Geometry = GetMouseGeometry(Length,Density,Sym)
            % Sensroy Neurons Definition 
            % Load necessary data
            load('01_SpinalGeometryFiles\matGeometry.mat');
            load("01_SpinalGeometryFiles\matDescending.mat");
            load('01_SpinalGeometryFiles\matMuscleSeg.mat');
            load('03_SpinalCordGeneticsFiles\matCellInfo.mat');
            %% Parameters Related to types of cells
            [Types,ixt] = unique(RCTDCellTypes.type,'stable');
            Transmitter = RCTDCellTypes.transmitter(ixt);
            %% Parameters Related to the geometry
            if(Sym)
                matLayers = cat(1,matLayers,matLayers);
                weights = cat(1,weights,weights);
                
                RCTDCoordFlip = RCTDCoord;
                RCTDCoord.x =  RCTDCoord.x-min(RCTDCoord.x,[],1)+1;
                RCTDCoord.y =  RCTDCoord.y-min(RCTDCoord.y,[],1)+1;
    
                RCTDCoordFlip.x = max(RCTDCoordFlip.x,[],1)-RCTDCoordFlip.x+1;
                RCTDCoordFlip.y = RCTDCoordFlip.y-min(RCTDCoordFlip.y,[],1)+1;
                RCTDCoord = cat(1,RCTDCoord,RCTDCoordFlip);
            end


            WhiteMat = strcmpi(matLayers.lowres,'white');
            GreyMat = strcmpi(matLayers.lowres,'grey');
            SensoryMat = strcmpi(matLayers.lowres,'DRG');

            GreyMat = GreyMat | SensoryMat;
            
            RCTDCoord.x =  RCTDCoord.x-min(RCTDCoord.x,[],1)+1;
            RCTDCoord.y =  RCTDCoord.y-min(RCTDCoord.y,[],1)+1;
        
            convfactor = 3500/range(RCTDCoord.x);
            RCTDCoord.x = (RCTDCoord.x).*convfactor;
            RCTDCoord.y = (RCTDCoord.y).*convfactor;

            GMCoords = RCTDCoord(GreyMat,2:3);
            WMCoords = RCTDCoord(WhiteMat,2:3);
            
            IdLayers = matLayers(GreyMat,:);
            WMIdLayers = matLayers(WhiteMat,:);
            ML = mean(RCTDCoord.x);
            GMLatera = (-1)*(GMCoords.x < ML) + (GMCoords.x >= ML);
            WMLatera = (-1)*(WMCoords.x < ML) + (WMCoords.x >= ML);

            if(isnumeric(Length))
                SegPos = 0;
                SegLength = Length;
                Length = nan;
                isSeg = 0;
            elseif(iscell(Length) || isstring(Length))
                Seg = ismember(Segments,Length);
                CumuLength = cumsum(SegmentLength);
                SegPos = CumuLength(Seg);
                SegLength = SegmentLength(Seg);
                isSeg = 1;
            else 
                error('Length must be either a numeric value in um or an string array of the segment to include');
            end
            
            %% Preprocessing of attribution weights before building geometry
            w = full(weights);
            wn = w(GreyMat,:);
            wn(wn==0) = min(wn(wn>0));
            wn = normalize(log(wn),1,'range');
            th = 0.4;
            %% Perform Classwise attribution
            rrc = [];
            res = [];
            Lat = [];
            Desc = [];
            Id = [];
            trans = [];
            for i = 1:length(Types)
               whr = CellTypesCensus.Cluster == Types(i);
               Type = CellTypesCensus.Type(whr);
               s = RandStream('mt19937ar','Seed',100,'NormalTransform','Polar');
               [swno,wnio] = sort(wn(:,i));
               cdwn = diff(cumsum(swno));
               ix = find(cdwn > th)+1;
               wni = wnio(ix);
               swn = swno(ix);
               gmlat = GMLatera(wnio);
               gmlat = gmlat(ix);
               swn = normalize(swn,'zscore');
               %% Detect 2% of cells expressing subtype genetic features
               indx = swn>1;  % Setting the threshold for detection
               indxl = indx & (gmlat>0);
               indxr = indx & (gmlat<0); 
               if(contains(string(Types(i)),'NF') | contains(string(Types(i)),'NP') | contains(string(Types(i)),'PEP') | contains(string(Types(i)),'TH') | contains(string(Types(i)),'MN'))
                   Dens = 1*Density;
               else
                   Dens = Density;
               end
               truevl = randsample(s,wni(indxl),ceil(length(wni(indx))*Dens),'true',normpdf(swn(indxl)),[],"all"); % Sample 75% of total
               truevr = randsample(s,wni(indxr),ceil(length(wni(indx))*Dens),'true',normpdf(swn(indxr)),[],"all"); % Sample 75% of total
               truev = [truevl;truevr];
               %% Detect Outliers in spatial distribution 
               [B,TF] = rmoutliers(GMCoords(truev,2),'median');     
               truev = truev(~TF);
               towrite = categorical(numel(truev),1);
               switch Type
                   case 'V3'
                       ind = true(numel(truev),1);
                       isV3 = IdLayers{truev,3} == '8Sp' | IdLayers{truev,3} == '7Sp' | IdLayers{truev,3} == 'Ps9' ;
                       towrite(ind) = categorical("V3-Dor");
                       towrite(isV3) = categorical("V3");
                       towrite = towrite';
                   case 'DI6'
                       ind = true(numel(truev),1);
                       isdI6 = IdLayers{truev,3} == '8Sp'| IdLayers{truev,3} == 'Ps9';
                       towrite(ind) = categorical("V1");
                       towrite(isdI6) = categorical("DI6");
                       towrite = towrite';
                   case 'MN'
                       truev = truev((IdLayers{truev,3} == 'Ad9' | IdLayers{truev,3} == 'CFl9' | IdLayers{truev,3} == 'Q9' | IdLayers{truev,3} == 'Ps9' | IdLayers{truev,3} == '8Sp'));
                       towrite = repelem(Type,numel(truev))';
                   otherwise
                    towrite = repelem(Type,numel(truev))';              
               end
               %% Part of the code to the adjust relative densities of specific cell types in the model
               % if(any(ismember(unique(towrite),'V2a-1')))
               %     p = ismember(towrite,'V2a-1');
               %     p = p*0.01;
               %     p(p==0) = 1;
               %     [ixtw]=logical(binornd(1,p));
               %     towrite = towrite(ixtw);
               %     truev = truev(ixtw);
               % end
               %% Populate Matrices for further computations
               res = [res; towrite];
               rrc = [rrc; table2array(GMCoords(truev,:))] ; 
               Lat = [Lat; GMLatera(truev)];
               trans = [trans; ones(length(truev),1).*Transmitter(i)];
               Id =  [Id; table2array(IdLayers(truev,{'highres','medres','lowres'}))];
            end   
            %% Build 3D spatial distribution
            WMCoords3D = [];
            Coords3D = [];
            Res3D = [];
            Id3D = [];
            WMId3D = [];
            Lat3D = [];
            WMLat3D = [];
            Transmit3D = [];
            Muscles3D = [];
            if(isSeg)
                MSS = ismember(MuscleSeg.Properties.VariableNames,categorical(Length));
                TotMN  = MuscleSeg.Variables;
                TotMN = sum(TotMN(:,MSS),'all')/3;
            end
            for i = 1:length(SegPos)
                %% Random Samplig of cells to include to maintain sparsity dependent on length definition
                WMI = randsample(1:size(WMCoords,1),round(size(WMCoords,1)/length(SegPos)),false);
                if(isSeg)
                    MIS = [categorical(MuscleSeg(MuscleSeg{:,Length(i)} ~=0,Length(i)).Row(:))];
                    PIS = MuscleSeg(MuscleSeg{:,Length(i)} ~=0,Length(i)).Variables;
                    Ax = MIS == 'Axial';
                    Limb = ~(Ax);

                    CMI = randsample(find(res~='MN'&Id(:,3)=='grey'),round(nnz(res~='MN'&Id(:,3)=='grey')/length(SegPos)),false);
                    CMI = [CMI;randsample(find(Id(:,3)=='DRG'),round(sum(PIS)/TotMN*(nnz(Id(:,3)=='DRG'))),true)];
                    CMI = [CMI;randsample(find(res=='MN'),round(sum(PIS)/TotMN*(nnz(res=='MN'))),true)];

                    AxId = Id(CMI,1) == 'Ps9' | Id(CMI,1) == '8Sp';
                    LimbId  =  Id(CMI,1) == 'Ad9' | Id(CMI,1) == 'Q9' |  Id(CMI,1) == 'CFl9' ;
                    MN = res(CMI) == 'MN';
                    LatL = Lat(CMI) > 0;
                    LatR = Lat(CMI) < 0;

                    Muscles = categorical(nan(size(CMI)));
                    if(nnz(Ax))
                        Muscles(MN & AxId & LatL) = randsample(MIS(Ax),nnz(MN & AxId & LatL),true);
                        Muscles(MN & AxId & LatR) = randsample(MIS(Ax),nnz(MN & AxId & LatR),true);
                    else
                        CMI(MN & AxId) = nan;
                    end
                    if(nnz(Limb))
                        Muscles(MN & LimbId & LatL) = randsample(MIS(Limb),nnz(MN & LimbId & LatL),true,PIS(Limb)/sum(PIS(Limb),'all'));
                        Muscles(MN & LimbId & LatR) = randsample(MIS(Limb),nnz(MN & LimbId & LatR),true,PIS(Limb)/sum(PIS(Limb),'all'));
                    else
                        CMI(MN & LimbId) = nan;
                    end
                    CMItemp = CMI;
                    CMI(isnan(CMItemp)) = [];
                    Muscles(isnan(CMItemp)) = [];
                else
                    CMI = randsample(1:size(rrc,1),round(size(rrc,1)/length(SegPos)),false);
                    Muscles = categorical(nan(size(res(CMI))));
                end

                Muscles3D = [Muscles3D; Muscles];
                WMCoords3D = [WMCoords3D; [table2array(WMCoords(WMI,:)), SegPos(i)-rand(size(WMCoords(WMI,1)))*SegLength(i)]];
                Coords3D = [Coords3D; [rrc(CMI,:) SegPos(i)-rand(size(rrc(CMI,1)))*SegLength(i)]];
                Res3D = [Res3D; res(CMI)];
                Id3D = [Id3D; [Id(CMI,:),repmat(Length(i),[length(CMI) 1])]];
                WMId3D = [WMId3D; [table2array(WMIdLayers(WMI,{'highres','medres','lowres'})),repmat(Length(i),[length(WMI) 1])]];
                Transmit3D = [Transmit3D; trans(CMI)];
                Lat3D = [Lat3D; Lat(CMI)];
                WMLat3D = [WMLat3D; WMLatera(WMI)];
                clear Ax Limb MN CMI WMI CMItemp
            end
            WMCoords3D = WMCoords3D + normrnd(0,10,size(WMCoords3D));
            Coords3D = Coords3D + normrnd(0,10,size(Coords3D));
            % Correct orientation and center orientation
            Coords3D(:,3) = Coords3D(:,3)-min(Coords3D(:,3));
            WMCoords3D(:,3) = WMCoords3D(:,3)-min(WMCoords3D(:,3));
            Coords3D(:,1) = Coords3D(:,1)-mean(WMCoords3D(:,1));
            WMCoords3D(:,1) = WMCoords3D(:,1)-mean(WMCoords3D(:,1));
            Coords3D(:,2) = -Coords3D(:,2);
            WMCoords3D(:,2) = -WMCoords3D(:,2);
      

            %% Final Attribution to output variables
            Geometry = table();
            Geometry.Position = [WMCoords3D(:,[1 3 2]);Coords3D(:,[1 3 2])];
            Geometry.Latera = [WMLat3D;Lat3D];
            Geometry.Layers = [WMId3D;Id3D];
            Geometry.Type = [repelem(categorical("WM"),length(WMLat3D))';Res3D];
            Geometry.Transmit = [zeros(length(WMLat3D),1);Transmit3D];
            Geometry.MnID = [categorical(nan(size(WMLat3D)));Muscles3D];
            Geometry.FlexExtID = [categorical(nan(size(WMLat3D))); categorical(nan(size(Muscles3D)))];
            if(isSeg)
                ANS = cellfun(@(x) find(ismember(MuscleSeg.Row,x)),cellstr(Geometry.MnID),'UniformOutput',false);
                tf = cellfun('isempty',ANS);
                ANS(tf) = {1};
                Geometry.FlexExtID = FlexExt(cell2mat(ANS))';
            end
            %%
            DescMat = strings(size(Geometry.Position(:,1)));
            DescMat(inROI(MedialVestibuloR,Geometry.Position(:,1),Geometry.Position(:,3))) =  strcat(DescMat(inROI(MedialVestibuloR,Geometry.Position(:,1),Geometry.Position(:,3))),repmat('MedVest',size(DescMat(inROI(MedialVestibuloR,Geometry.Position(:,1),Geometry.Position(:,3))))));
            DescMat(inROI(MedialVestibuloL,Geometry.Position(:,1),Geometry.Position(:,3))) =  strcat(DescMat(inROI(MedialVestibuloL,Geometry.Position(:,1),Geometry.Position(:,3))),repmat('MedVest',size(DescMat(inROI(MedialVestibuloL,Geometry.Position(:,1),Geometry.Position(:,3))))));
            DescMat(inROI(CorticospinalR,Geometry.Position(:,1),Geometry.Position(:,3))) =  strcat(DescMat(inROI(CorticospinalR,Geometry.Position(:,1),Geometry.Position(:,3))),repmat('Cortico',size(DescMat(inROI(CorticospinalR,Geometry.Position(:,1),Geometry.Position(:,3))))));
            DescMat(inROI(CorticospinalL,Geometry.Position(:,1),Geometry.Position(:,3))) =  strcat(DescMat(inROI(CorticospinalL,Geometry.Position(:,1),Geometry.Position(:,3))),repmat('Cortico',size(DescMat(inROI(CorticospinalL,Geometry.Position(:,1),Geometry.Position(:,3))))));
            DescMat(inROI(MedullalryReticulospinalR,Geometry.Position(:,1),Geometry.Position(:,3))) =  strcat(DescMat(inROI(MedullalryReticulospinalR,Geometry.Position(:,1),Geometry.Position(:,3))),repmat('MedReticulo',size(DescMat(inROI(MedullalryReticulospinalR,Geometry.Position(:,1),Geometry.Position(:,3))))));
            DescMat(inROI(MedullalryReticulospinalL,Geometry.Position(:,1),Geometry.Position(:,3))) =  strcat(DescMat(inROI(MedullalryReticulospinalL,Geometry.Position(:,1),Geometry.Position(:,3))),repmat('MedReticulo',size(DescMat(inROI(MedullalryReticulospinalL,Geometry.Position(:,1),Geometry.Position(:,3))))));
            DescMat(inROI(PontineReticuloR,Geometry.Position(:,1),Geometry.Position(:,3))) =  strcat(DescMat(inROI(PontineReticuloR,Geometry.Position(:,1),Geometry.Position(:,3))),repmat('PontReticulo',size(DescMat(inROI(PontineReticuloR,Geometry.Position(:,1),Geometry.Position(:,3))))));
            DescMat(inROI(PontineReticuloL,Geometry.Position(:,1),Geometry.Position(:,3))) =  strcat(DescMat(inROI(PontineReticuloL,Geometry.Position(:,1),Geometry.Position(:,3))),repmat('PontReticulo',size(DescMat(inROI(PontineReticuloL,Geometry.Position(:,1),Geometry.Position(:,3))))));
            DescMat(inROI(RubrospinalR,Geometry.Position(:,1),Geometry.Position(:,3))) =  strcat(DescMat(inROI(RubrospinalR,Geometry.Position(:,1),Geometry.Position(:,3))),repmat('Rubro',size(DescMat(inROI(RubrospinalR,Geometry.Position(:,1),Geometry.Position(:,3))))));
            DescMat(inROI(RubrospinalL,Geometry.Position(:,1),Geometry.Position(:,3))) =  strcat(DescMat(inROI(RubrospinalL,Geometry.Position(:,1),Geometry.Position(:,3))),repmat('Rubro',size(DescMat(inROI(RubrospinalL,Geometry.Position(:,1),Geometry.Position(:,3))))));
            DescMat(inROI(LPGIVglyR,Geometry.Position(:,1),Geometry.Position(:,3))) =  strcat(DescMat(inROI(LPGIVglyR,Geometry.Position(:,1),Geometry.Position(:,3))),repmat('LPGIgly',size(DescMat(inROI(LPGIVglyR,Geometry.Position(:,1),Geometry.Position(:,3))))));
            DescMat(inROI(LPGIVglyL,Geometry.Position(:,1),Geometry.Position(:,3))) =  strcat(DescMat(inROI(LPGIVglyL,Geometry.Position(:,1),Geometry.Position(:,3))),repmat('LPGIgly',size(DescMat(inROI(LPGIVglyL,Geometry.Position(:,1),Geometry.Position(:,3))))));
            DescMat(inROI(LPGIVglutR,Geometry.Position(:,1),Geometry.Position(:,3))) =  strcat(DescMat(inROI(LPGIVglutR,Geometry.Position(:,1),Geometry.Position(:,3))),repmat('LPGIglut',size(DescMat(inROI(LPGIVglutR,Geometry.Position(:,1),Geometry.Position(:,3))))));
            DescMat(inROI(LPGIVglutL,Geometry.Position(:,1),Geometry.Position(:,3))) =  strcat(DescMat(inROI(LPGIVglutL,Geometry.Position(:,1),Geometry.Position(:,3))),repmat('LPGIglut',size(DescMat(inROI(LPGIVglutL,Geometry.Position(:,1),Geometry.Position(:,3))))));
            DescMat(inROI(RapheObsR,Geometry.Position(:,1),Geometry.Position(:,3))) =  strcat(DescMat(inROI(RapheObsR,Geometry.Position(:,1),Geometry.Position(:,3))),repmat('RapheObs',size(DescMat(inROI(RapheObsR,Geometry.Position(:,1),Geometry.Position(:,3))))));
            DescMat(inROI(RapheObsL,Geometry.Position(:,1),Geometry.Position(:,3))) =  strcat(DescMat(inROI(RapheObsL,Geometry.Position(:,1),Geometry.Position(:,3))),repmat('RapheObs',size(DescMat(inROI(RapheObsL,Geometry.Position(:,1),Geometry.Position(:,3))))));
            Geometry.Descending = DescMat;
        end
    end

    methods(Static,Access=private)
        function towrite = AssignCellType(Type,truev)    
        end
    end
end