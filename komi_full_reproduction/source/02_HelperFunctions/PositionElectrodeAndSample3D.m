function [NOI,varargout] = PositionElectrodeAndSample3D(ElectrodeMap,Pos,InsertionLength,neuronlocation,varargin)
rotangle = nan;
DistThresh = 50;
for ii = 1:2:length(varargin)
    switch varargin{ii}
        case 'rotate'
            rotangle = varargin{ii + 1};
            rotX = rotx(rotangle(1));
            rotY = roty(rotangle(2));
            rotZ = rotz(rotangle(3));
        case 'DistThresh'
            DistThresh = varargin{ii+1};
    end
end

ElectrodePos(:,1) = ElectrodeMap(:,1);
ElectrodePos(:,2) = ElectrodeMap(:,2);
ElectrodePos(:,3) = 0;

RElectrodePos = ElectrodePos;
if(~isnan(rotangle))
    X = RElectrodePos(:,1);
    Y = RElectrodePos(:,2);
    Z = RElectrodePos(:,3);
    ang = rotangle;  % degrees

    Xc = mean(X);
    Yc = mean(Y);
    Zc = mean(Z);

    X = X-Xc;
    Y = Y-Yc;
    Z = Z-Zc;

    torot = [X,Y,Z];
    outrot = ((torot*rotX)*rotY)*rotZ;

    RElectrodePos(:,1) =  outrot(:,1);
    RElectrodePos(:,2) =  outrot(:,2);
    RElectrodePos(:,3) =  outrot(:,3) + range(outrot(:,3))/2;

    % Mediolaterl Positioning
    RElectrodePos(:,1) =  RElectrodePos(:,1) + Pos(1);
    RElectrodePos(:,2) =  RElectrodePos(:,2) + Pos(2);
    RElectrodePos(:,3) =  RElectrodePos(:,3) + Pos(3);

    % Insertion Depth
    dirvec = (RElectrodePos(1,:)-RElectrodePos(end-1,:));
    dirvec = dirvec./norm(dirvec);
    Insertion = dirvec*InsertionLength;
    RElectrodePos = RElectrodePos+Insertion;

end


for ii = 1:length(RElectrodePos)
    for jj = 1:length(neuronlocation)
        Dist(ii,jj) = sqrt((RElectrodePos(ii,1)-neuronlocation(jj,1)).^2 + (RElectrodePos(ii,2)-neuronlocation(jj,2)).^2 + (RElectrodePos(ii,3)-neuronlocation(jj,3)).^4 );
        %Dist(ii,jj) = sqrt((RElectrodePos(ii,1)-neuronlocation(jj,1)).^2 + (RElectrodePos(ii,2)-neuronlocation(jj,2)).^2);
    end
end

IsIn = ~(RElectrodePos(:,3) >= 0);
LogicalDist = (Dist < DistThresh) & IsIn ;

for jj = 1:size(Dist,2)
    ClusterChan(jj) = find(Dist(:,jj) == min(Dist(IsIn,jj))); %size(Dist,1) - +1;
end
%ClusterChan = (size(LogicalDist,1) - ClusterChan)+1;
NOI = logical(sum(LogicalDist,1))' ;
varargout = {RElectrodePos,ElectrodePos,ClusterChan};
end