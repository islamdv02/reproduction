function C = GetNetworkColors(N)
    DorPop = unique(N.Types(N.Layers == 'DRG'|N.Layers == '1Sp'| N.Layers == '2Sp0' | N.Layers == '2SpI' | N.Layers == '3Sp' | N.Layers == '4Sp'),'sorted');
    VentrPop = unique(N.Types(N.Layers == '5Spm'|N.Layers == '5SpL'| N.Layers == '6SpM' | N.Layers == '6SL' | N.Layers == '7Sp' | N.Layers == '8Sp' | N.Layers == 'D' | N.Layers == '10Sp' | N.Layers == 'Ps9'),'sorted');
    MN = unique(N.MnID(~isundefined(N.MnID)));

    cmapdorsal = fliplr(autumn(length(DorPop)));  
    cmapventralex = flipud(cool(length(VentrPop))); 
    cmapventralin = cool(length(VentrPop));
    cmapmn = sky(length(MN)); 

    C = zeros(size(N.ConnMat,1),3);

    for T = 1:length(DorPop)
        whr = N.Types == DorPop(T);
        C(whr,:) = repmat(cmapdorsal(T,:),[nnz(whr),1]);
    end
    
    for T = 1:length(VentrPop)
        whr = N.Types == VentrPop(T);
        if(mean(N.Transmit(whr)) < 0)
            C(whr,:) = repmat(cmapventralin(T,:),[nnz(whr),1]);
        else 
            C(whr,:) = repmat(cmapventralex(T,:),[nnz(whr),1]);
        end
    end  

    for T = 1:length(MN)
        whr = N.MnID == MN(T);
        C(whr,:) = repmat(cmapmn(T,:),[nnz(whr),1]);
    end
end