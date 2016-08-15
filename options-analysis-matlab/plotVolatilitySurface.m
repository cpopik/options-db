% Plot implied volatility surface for specific ticker
ticker = 'AAPL';
type = 'CALL';
var = 'bsVol';
date = datenum('8/2/16');

% ESTABLISH DATABASE CONNECTION
conn = database('options','admin','servire87','Vendor','MySQL','Server','www.derivs.xyz');
query = ['SELECT expiry, strike, ' var ', underlying FROM options.$' ticker ' WHERE type = ''' type ''' AND bsVol != 0 AND date = ' num2str(date) ';'];

% RETURN THE DATA FROM THE DATABASE
curs = exec(conn, query);
curs = fetch(curs);
d = cell2mat(curs.Data);

% REDEFINE DATES TO DAYS
d(:,1) = d(:,1) - today;
% MONEYNESS
d(:,2) = d(:,2)./d(:,4);

% LINEAR INTERPOLANT
resDays = 7;
resMoneyness = (max(d(:,2))-min(d(:,2)))/50;
maxDays = 100;
[Y,X] = meshgrid(min(d(:,1)):resDays:maxDays, min(d(:,2)):resMoneyness:max(d(:,2)));
Z = griddata(d(:,1),d(:,2),d(:,3),Y,X, 'linear');

% PLOT VOL SURFACE
figure(1)
surf(X,Y+today,Z)
view(20,30);
datetick('y','mm-dd-yy')
set(gca,'fontsize',14)
title([ticker ' ' type], 'FontSize', 18, 'FontWeight', 'Bold')
xlabel('Moneyness', 'FontSize', 16, 'FontWeight', 'Bold')
ylabel('Expiry', 'FontSize', 16, 'FontWeight', 'Bold')
zlabel(var, 'FontSize', 16, 'FontWeight', 'Bold')









