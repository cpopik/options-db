% Plot implied volatility surface for specific ticker
ticker = 'AAPL';
type = 'CALL';
var = 'bsVol';
date = today;

% ESTABLISH DATABASE CONNECTION
conn = database('options','admin','servire87','Vendor','MySQL','Server','www.derivs.xyz');
query = ['SELECT date, dte, bsVol FROM (SELECT (expiry - date) AS dte, (strike - underlying) AS diff, bsVol, type, date, strike, expiry FROM options.$' ticker ') AS a WHERE type = ''' type ''' AND a.bsVol != 0 AND a.diff BETWEEN 0 and .5 GROUP BY type, date, dte;'];

% RETURN THE DATA FROM THE DATABASE
curs = exec(conn, query);
curs = fetch(curs);
d = cell2mat(curs.Data);
dateList = min(d(:,1)):1:max(d(:,1));
% remove weekends
dateList = dateList(ismember(weekday(dateList), [2 3 4 5 6]));


out = [];
for date = dateList
    active = d([d(:,1) == date],:);
    
    iv30 = NaN;
    iv60 = NaN;
    iv90 = NaN;
    
    if length(active) > 0
        dte = active(:,2);
        vol = active(:,3);
        xq = min(dte):1:max(dte);
        interp = interp1(dte,vol,xq);

        iv30 = interp([xq == 30]);
        iv60 = interp([xq == 60]);
        iv90 = interp([xq == 90]);
    end
    
    if isempty(iv30); iv30 = NaN; end
    if isempty(iv60); iv60 = NaN; end
    if isempty(iv90); iv90 = NaN; end
    
    out = [out; date, iv30, iv60, iv90];
end

plot(out(:,1), out(:,2), '-r')
datetick('x','mm-dd-yy')









