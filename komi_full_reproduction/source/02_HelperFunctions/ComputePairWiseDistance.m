function DistanceMatrix = ComputePairWiseDistance(Coord)
    P = [Coord(:,1) Coord(:,2) Coord(:,3)];
    DistanceMatrix = zeros(length(P),length(P));
    for i = 1:length(P)
        for j = 1:length(P)
            DistanceMatrix(i,j) = sqrt((P(i,1)-P(j,1)).^2 + (P(i,2)-P(j,2)).^2 + (P(i,3)-P(j,3)).^2);
        end
    end
end