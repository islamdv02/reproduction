function Connectivity = BalanceConnectivity(Connectivity,varargin)
    % Balance Network
    for ii = 1:size(Connectivity,1)
        balance = sum(Connectivity(ii,:));
        jjpos = find(Connectivity(ii,:)>0);
        jjneg = find(Connectivity(ii,:)<0);

        bp = sum(Connectivity(ii,jjpos))-(balance/2);
        bn = sum(Connectivity(ii,jjneg))-(balance/2);

        facp = bp/sum(Connectivity(ii,jjpos));
        facn = bn/sum(Connectivity(ii,jjneg));

        Connectivity(ii,jjpos) = Connectivity(ii,jjpos)*facp; 
        Connectivity(ii,jjneg) = Connectivity(ii,jjneg)*facn; 
    end    
end
