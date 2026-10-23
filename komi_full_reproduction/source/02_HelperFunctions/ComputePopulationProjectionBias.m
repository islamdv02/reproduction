function PopProjBias = ComputePopulationProjectionBias(Geometry,Parameters)
    PopProjBias = zeros(size(Geometry,1),size(Geometry,1));
    for s = Parameters.Types  
        si = Parameters.Types == s;
        for t = Parameters.Types  
            try
            ti = Parameters.Types == t;
            PopProjBias((Geometry.Type == t)&(Geometry.Type == s)') = Parameters.BiasPop(ti'&si);
            catch e
                e.message
            end
        end
    end
end