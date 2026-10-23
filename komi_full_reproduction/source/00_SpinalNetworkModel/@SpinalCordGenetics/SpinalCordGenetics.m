classdef SpinalCordGenetics 
    methods (Static) 
        function Genetics = GetMouseGenetics(Sym) 
            load('03_SpinalCordGeneticsFiles\matCountSpatialScaled.mat')
            load('03_SpinalCordGeneticsFiles\matCountSingleCell.mat')
            load('03_SpinalCordGeneticsFiles\matRCTD.mat') 
            load('01_SpinalGeometryFiles\matGeometry.mat');
            load("03_SpinalCordGeneticsFiles\matCellInfo.mat")
            Genetics.Counts = CountSpatial;
            Genetics.Genes = GenesSpatial;
            Genetics.Weights = weights;
            Genetics.Types = RCTDTypes;    
            Genetics.Coords = RCTDCoord;
            Genetics.Census = CellTypesCensus;
            Genetics.CountsSC = CountSingleCell;
            Genetics.TypesSC = Types;
            Genetics.GenesSC = Genes;
            Genetics.LineageSC = Lineage;
        end
    end
end
