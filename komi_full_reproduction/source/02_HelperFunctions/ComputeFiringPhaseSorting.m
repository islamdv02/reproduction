function [SortingIndices,varargout] = ComputeFiringPhaseSorting(FiringMatrix,varargin)
    Method = 'Correlation';
    Var = var(FiringMatrix,1);
    [~,ix] = max(Var);
    Source = FiringMatrix(:,ix);
    for ii = 1:2:length(varargin)
        switch(varargin{ii})
            case 'Source'
                Source = varargin{ii+1};
            case 'Method'
                Method = varargin{ii+1};
        end
    end

    switch Method 
        case 'Correlation'
           % whole = FiringMatrix(:,15);
            whole = Source; 
            scores = [];
            corrs = [];
            for n = 1:size(FiringMatrix,2)
                [C,L] = xcorr(whole,FiringMatrix(:,n));
                [maxVal,loc] = max(C);
                scores = [scores L(loc)];
                corrs = [corrs maxVal];
            end
            
            [autocor,~] = xcorr(whole);
            [~,lcsh] = findpeaks(autocor);
            short = mean(diff(lcsh));
           

            scores =rem((scores.*2*pi)./short,2*pi);
            corrs = corrs./max(autocor);
            
            [scoresS,CorrSorting] =  sort(scores,'ascend');
            SortingIndices = CorrSorting;
            varargout = {scores,corrs};
    end
end
