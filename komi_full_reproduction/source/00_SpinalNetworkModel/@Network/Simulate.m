function Simulate(obj,t_steps,varargin)
    [~,IxT] = ismember(obj.Types,obj.Parameters.Types);
    W = obj.ConnMat;
    f_V_func = @tanh_f_V;  %@sigm_f_V;%
    tau_V = ones(size(W,1),t_steps)*50;% Slower Excitation
    isAd = obj.GetNeuronsInDiffGeneExpSingleCell('Kcnn','LogFCThreshold',1);   
    tau_a = ones(size(W,1),t_steps)*100000000000;% Slower Adaptation
    tau_a(isAd,:) = 3000; % Faster Inhibition
    tau_a(~isAd,:) = 10000; % Faster Inhibition
    noise_ampl = 0.5;
    seed = 5;
    I_e = ones(size(W,1),t_steps)*25;
    V_init = -70;
    threshold = repmat(obj.Parameters.Thresholds(IxT)',[1 t_steps]);
    gain = repmat(obj.Parameters.Gains(IxT)',[1 t_steps]);
    f_max = obj.Parameters.F_max(IxT)';
    Ad = 0;
    Ca = 1.25;

    for ii = 1:2:length(varargin)
        switch varargin{ii}
            case 'tau_V'
                tau_V = varargin{ii+1};
            case 'tau_a'
                tau_a = varargin{ii+1};
            case 'noise_ampl'
                noise_ampl = varargin{ii+1};
            case 'seed'
                seed = varargin{ii+1};
            case 'I_e'
                I_e = varargin{ii+1};
            case 'V_init'
                V_init = varargin{ii+1};
            case 'threshold'
                threshold = varargin{ii+1};
            case 'gain'
                gain = varargin{ii+1};
            case 'fmax'
                f_max = varargin{ii+1};
            case 'Adaptation'
                Ad = varargin{ii+1};
        end
    end

    rng(seed);
    N = size(W,1);
    R = zeros(t_steps, N);  
    a = zeros(N, t_steps);
    V = zeros(N, t_steps);
    V(:, 1) = normrnd(V_init,3,size(V(:, 1)));
    R(1, :) = zeros(size(V_init));
    I_noise = normrnd(0.,noise_ampl,[1 (t_steps)*N]);
    I_rec = zeros(N, t_steps);
    I_tot = zeros(N, t_steps);
    I_noise = reshape(I_noise,size(I_tot));


    tic
    for t = 2:t_steps
        I_rec(:,t-1) = W*R(t-1,:)';
        I_tot(:,t-1) = I_rec(:,t-1) + I_noise(:,t-1) + I_e(:,t-1);
        dV = (-V(:,t-1) + I_tot(:,t-1))./tau_V(:,t-1);
        V(:,t) = V(:,t-1) + dV;
        if(Ad)
            da = (Ca*R(t-1,:)'-a(:,t-1))./tau_a(:,t-1);
            a(:,t) = a(:,t-1) + da;
        end
        R(t, :) = f_V_func(V(:,t)-a(:,t), threshold(:,t), gain(:, t), f_max);
    end
    toc
    
    obj.Rates = R;
    obj.Voltage = V';
end

%% Helper Functions 
function val = tanh_f_V(V,threshold,gain,fmax) %20,1,100
    f = zeros(1,size(V,1)); 
    neg = (V-threshold)<=0.;
    pos = (V-threshold)>0;
    f(neg) = threshold(neg).*tanh(gain(neg).*(V(neg)-threshold(neg))./threshold(neg));
    f(pos) = fmax(pos).*tanh(gain(pos).*(V(pos)-threshold(pos))./fmax(pos));        
    val = f+threshold';
end
