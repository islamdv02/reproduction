%% Function Library
function [GFiring,SpikeTrain] = GetGaussianFiring(SpikeTrain,w,fs)
    %% Define Gaussian Window
    GFiring = [];
    theta = (w*fs)/1000;
    t = -4*theta:theta*4;
    kt = (1000/(sqrt(2*pi)*w))*exp(-(t.^2/(2*theta^2)));
    for i = 1:size(SpikeTrain,2)
        GFiring(:,i) = conv(kt,SpikeTrain(:,i));
    end
    GFiring = GFiring(floor(length(t)/2):size(GFiring,1)-ceil(length(t)/2),:);
end