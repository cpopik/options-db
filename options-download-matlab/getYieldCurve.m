% Interpolate the yield curve using Yahoo Finance data

function [zeroDates, zeroRates] = getYieldCurve()

    % DOWNLOADING CURVE DATA FROM YAHOO
    T30Y = fetch(yahoo, '^TYX');
    T10Y = fetch(yahoo, '^TNX');
    T5Y = fetch(yahoo, '^FVX');
    T13W = fetch(yahoo, '^IRX');

    data = [T13W.Last T5Y.Last T10Y.Last T30Y.Last]/100;
    dates = daysadd(today,[7*13 360*5 360*10 360*30],1);
    irdc = IRDataCurve('zero', today, dates, data, 'InterpMethod','pchip');

    % MORE GRANULAR DAYS AND RATES
    zeroDates = daysadd(today,1:10:30*360,1);
    zeroRates = getZeroRates(irdc, zeroDates);

end

