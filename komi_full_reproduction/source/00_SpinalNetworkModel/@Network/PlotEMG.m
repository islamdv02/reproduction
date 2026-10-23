function  PlotEMG(obj,varargin)
    Moi = unique(obj.MnID);
    Moi(isundefined(Moi)) = [];
    TOI = 1:size(obj.Rates,1);
    Side = 'R';
    Ref = 'Vastus Medialis';

    for ii = 1:2:length(varargin)
        switch varargin{ii}
            case 'MN'
               Moi = categorical(varargin{ii+1})';
            case 'TOI'
               TOI = varargin{ii+1};
            case 'Side'
                Side = varargin{ii+1};
            case 'Segment'
                Segment = varargin{ii+1};
        end
    end

    if(strcmpi(Side,'L'))
        ixref = obj.MnID == Ref & obj.Latera < 0;
    else
        ixref = obj.MnID == Ref & obj.Latera > 0;
    end
    ref = mean(obj.Rates(TOI,ixref),2);
    ref = ref-median(ref(0.1*length(ref):end));
    ref(ref < 0) = 0;
    ref(ref > 0)= 1;


    noiselevel= 0.1;
    jj = 1;
    screensize = get(groot,'ScreenSize');
     figure(Color='white',Position=screensize);

    axis tight
    for ii = Moi'
        if(~isundefined(ii))
            if(strcmpi(Side,'L'))
                ix = obj.MnID==ii & obj.Latera < 0;
            else
                ix = obj.MnID==ii & obj.Latera > 0;
            end

            if(ismember(obj.FlexExtID(ix),'Ext'))
                Col = Colors().BergOrange;
            elseif (ismember(obj.FlexExtID(ix),'Flex'))
                Col = Colors().BergBlue;
            else
                Col = Colors().BergWhite;
            end

            prob = sum(obj.Rates(TOI,ix),2);
            sig = randn(size(prob))*noiselevel.*binornd(1,normcdf(normalize(prob,'zscore')));
            sig = sig.*prob  + (randn(size(prob))*noiselevel) ;

            ax = gca;
            off =ax.YLim(2)+range(sig)/2;
            plot(sig+off,'Color',[Colors().BergBlack 0.5]);
            hold on
            plot(-movmean(abs(sig),20)+off,'Color',Col,'LineWidth',2.5);
            jj = jj+1;
        end
    end

    hold on
    [~,locs] =  findpeaks(abs(diff(ref)));
    for n = 1:2:length(locs)-1 
        patch([locs(n) locs(n+1) locs(n+1) locs(n)],[0 0 max(ax.YLim) max(ax.YLim)],[0 0 0],'FaceAlpha',0.3,'FaceColor',Colors().BergGray02,'EdgeColor','none')
    end

    c = lines(jj);
    colormap(c)
    set(gca, 'YDir','reverse')

 
    % jj= 1;
    % subplot(1,2,2)
    % axis tight
    % for ii = Moi'
    %     if(~isundefined(ii))
    %         ix = obj.MnID==ii & obj.Latera < 0;
    %         prob = sum(obj.Rates(:,ix),2);
    %         prob = (prob-min(prob));
    %         sig = randn(size(prob))*noiselevel.*binornd(1,prob./range(prob));
    %         sig = normalize(sig.*prob,'norm');
    %         ax = gca;
    %         plot(sig+ax.YLim(2)+range(sig)/2);
    %         hold on
    %         jj = jj+1;
    %     end
    % end
    % c = lines(jj);
    % colormap(c)
    % set(gca, 'YDir','reverse')
    legend(Moi,'Location','northeastoutside');
end