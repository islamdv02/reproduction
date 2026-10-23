function  PlotNeurogram(obj,varargin)
    Moi = unique(obj.Segment);
    Moi(isundefined(Moi)) = [];
    TOI = 1:size(obj.Rates,1);
    Side = 'R';
    Ref = 'L2';
    Off = 0;
    Patch = 1;
    fig = [];
    ax = [];

    for ii = 1:2:length(varargin)
        switch varargin{ii}
            case 'TOI'
               TOI = varargin{ii+1};
            case 'Side'
                Side = varargin{ii+1};
            case 'Segment'
                Moi = categorical(varargin{ii+1})';
            case 'Tuple'
                Tup = varargin{ii+1};
            case 'Offset'
                Off = varargin{ii+1};
            case 'Figure'
                fig = varargin{ii+1};
            case 'Axis'
                ax = varargin{ii+1};
            case 'patch'
                Patch = varargin{ii+1};
        end
    end

    if(strcmpi(Side,'L'))
        ixref = obj.Segment == Ref & obj.Latera < 0;
    else
        ixref = obj.Segment == Ref & obj.Latera > 0;
    end
    ref = mean(obj.Rates(TOI,ixref),2);
    ref = ref-median(ref(0.1*length(ref):end));
    ref(ref < 0) = 0;
    ref(ref > 0)= 1;


    noiselevel= 0.1;
    jj = 1;
    screensize = get(groot,'ScreenSize');
    if(isempty(fig))
        fig = figure(Color='white',Position=screensize);
    else 
        figure(fig);
    end
    if(isempty(ax))
        ax = gca;
    end
    axis(ax);
    axis tight
    for ii = Moi'
        if(~isundefined(ii))
            if(strcmpi(Side,'L'))
                ix = obj.Segment==ii & obj.Types == 'MN' & obj.Latera < 0;
            else
                ix = obj.Segment==ii & obj.Types == 'MN' & obj.Latera > 0;
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
            

            off =ax.YLim(2)+range(sig)/2 + Off;
            plot(sig+off,'Color',[Colors().BergBlack 0.5]);
            hold on
            plot(-movmean(abs(sig),20)+off,'Color',Col,'LineWidth',2.5);
            jj = jj+1;
        end
    end

    if(Patch)
        hold on
        [~,locs] =  findpeaks(abs(diff(ref)));
        for n = 1:2:length(locs)-1 
            patch([locs(n) locs(n+1) locs(n+1) locs(n)],[0 0 max(ax.YLim) max(ax.YLim)],[0 0 0],'FaceAlpha',0.3,'FaceColor',Colors().BergGray02,'EdgeColor','none')
        end
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
    %strings = string(get(findobj(ax,'type','Legend'),'String'));
    %legend(ax,[strings,string(Moi)],'Location','northeastoutside');
end