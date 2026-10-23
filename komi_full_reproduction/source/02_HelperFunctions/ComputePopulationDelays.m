function Delays = ComputePopulationDelays(Geometry,Parameters)
    Delays = zeros(size(Geometry,1),size(Geometry,1));
    for s = Parameters.Types  
        si = Parameters.Types == s;
        for t = Parameters.Types  
            ti = Parameters.Types == t;
            Delays((Geometry.Type == t)&(Geometry.Type == s)') = Parameters.DelaysPop(ti'&si);
        end
    end
end