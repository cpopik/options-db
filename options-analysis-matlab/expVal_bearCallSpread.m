function value = expVal_bearCallSpread(k1, k2, p1, p2, spot, vol, daysTilExpiry)

    warning('off','all')

    % SCALE VOL
    vol = vol*sqrt(daysTilExpiry/360);
    r1 = log(k1/spot);
    r2 = log(k2/spot);
    m = -((p1-p2)-(k1-k2))/(r2-r1);

    lowBoundFunc = @(r) (p1-p2)*1/(vol*sqrt(2*pi))*exp(-r.^2/(2*vol^2));
    midBoundFunc = @(r) times(m*(r-r1), 1/(vol*sqrt(2*pi))*exp(-r.^2/(2*vol^2)));
    highBoundFunc =  @(r) (k1-k2)*1/(vol*sqrt(2*pi))*exp(-r.^2/(2*vol^2));

    value = 100*(integral(lowBoundFunc, -inf, r1) + integral(midBoundFunc, r1, r2) + integral(highBoundFunc, r2, inf));
    
    if (isnan(value))
        value = 0;
    end

end


