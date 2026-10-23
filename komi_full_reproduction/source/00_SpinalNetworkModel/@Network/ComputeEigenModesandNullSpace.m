function obj = ComputeEigenModesandNullSpace(obj,varargin)

        PopOfI = ones(size(obj.Types));
        LayerOfI = ones(size(obj.Layers));
        LatOfI =  ones(size(obj.Latera));
        TransOfI = ones(size(obj.Transmit));
        MNOfI = ones(size(obj.MnID));
        FEOfI = ones(size(obj.FlexExtID));
        SegOfI = ones(size(obj.Segment));
        UoI = ones(size(obj.Segment));
        verbose = 0;
        for ii = 1:2:length(varargin)
            switch varargin{ii}
                case 'Type'
                   PopOfI = contains(string(obj.Types),varargin{ii+1});
                case 'Layer'
                   LayerOfI = contains(string(obj.Layers),varargin{ii+1});
                case 'Latera'
                   LatOfI = obj.Latera == varargin{ii+1};
                case 'Transmit'
                   TransOfI = obj.Transmit == varargin{ii+1};
                case 'MNId'
                   MNOfI = obj.MnID == varargin{ii+1};
                case 'FlexExt'
                   FEOfI = obj.FlexExtID == varargin{ii+1};
                case 'Segment'
                   SegOfI = contains(string(obj.Segment),varargin{ii+1});           
                case 'SaveName'
                    Name = varargin{ii+1};
                case 'UoI'
                    UoI = varargin{ii+1};
                case 'Verbose'
                    verbose = varargin{ii+1};
            end
        end   
        
        TP = PopOfI&LayerOfI&LatOfI&TransOfI&MNOfI&FEOfI&SegOfI&UoI;

        [vec,bevr] = eig(obj.ConnMat,'vector');
        vec = real(vec);
        [brevr,bixev] = sort(real(bevr),'descend');
        bievr = imag(bevr(bixev));

        [~,ind] = unique(brevr,'stable');
    
        ixoi = find((brevr <= 0.01 )&(brevr >= -0.01));
        vecsort = vec(:,bixev);

        vecsum = zeros(size(vec(:,1)));
        for i = ixoi'
            vecsum = vecsum + vecsort(:,i);
        end
        vecsum(vecsum==0) = nan;
        obj.NullSpace = vecsum;
        obj.EigenValues = bevr(bixev);
        obj.EigenModes = [];
         for ii = 1:3
                obj.EigenModes(ii,:) = 100*normalize(real(vec(TP,bixev(ind(ii)))+abs(min(vec(TP,bixev(ind(ii)))))),'range')+0.01; 
         end

        if(verbose)
            screensize = get(groot,'ScreenSize');
            figure(Color=Colors().BergWhite,Position=[screensize(1) screensize(2) screensize(3)/2 screensize(4)]);           
            subplot(1,5,[1 2])
            scatter(brevr,bievr)
            vline(1)
            axis equal
    
            Seg = unique(obj.Segment(~isundefined(obj.Segment)));
            for ii = 1:3
                Col = (obj.EigenModes(ii,:)/100)'.*Colors().BergBlack  +  (1-obj.EigenModes(ii,:)/100)'.*Colors().BergWhite;
                h(ii) = subplot(1,5,2+ii);
                hold on
                scatter3(obj.Position(TP,1),obj.Position(TP,2),obj.Position(TP,3),obj.EigenModes(ii,:)/10,Col,"filled"); 

                for S = Seg'
                  [minb,maxb] = bounds(obj.Position(obj.Segment == S,2));
                  plot3([600 1200],[minb minb],[0 0]);
                  text(1250,minb+(maxb-minb)/2,0,S)
                end
                axis equal tight
            end
            linkaxes(h)
            
            %figure 
            %scatter3(obj.Position(:,1),obj.Position(:,2),obj.Position(:,3),10*abs(vecsum),Colors().BergBlack,"filled"); 
        end

end