ticker = 'SPY';
date = today-3;

% ESTABLISH DATABASE CONNECTION
conn = database('options','admin','servire87','Vendor','MySQL','Server','www.derivs.xyz');
queryCalls = ['SELECT expiry, strike, bsVol, (bid+ask)/2, underlying FROM options.$' ticker ' WHERE type = ''CALL'' AND bsVol != 0 AND date = ' num2str(date) ';'];
queryPuts = ['SELECT expiry, strike, bsVol, (bid+ask)/2, underlying FROM options.$' ticker ' WHERE type = ''PUT'' AND bsVol != 0 AND date = ' num2str(date) ';'];

% RETURN THE DATA FROM THE DATABASE
curs = exec(conn, queryCalls); curs = fetch(curs);
calls = cell2mat(curs.Data(:,1:5));
calls = calls((calls(:,1)-today) == 5,:);
calls = calls(mod(calls(:,2),1) == 0,:);

curs = exec(conn, queryPuts); curs = fetch(curs);
puts = cell2mat(curs.Data(:,1:5));
puts = puts((puts(:,1)-today) == 5,:);
puts = puts(mod(puts(:,2),1) == 0,:);

spot = calls(1,5);

% MAXIMUM ENTROPY MATRICES - CALLS
strikes = calls(:,2);
% EQUALS
prices = linspace(0, 2*spot, length(calls(:,1)) + length(puts(:,1))+100);
priceSpace = repmat(prices,length(strikes),1);
AeqCalls = [];
for i = 1:length(strikes)
    for j = 1:length(priceSpace)
        AeqCalls(i,j) = max(0, priceSpace(i,j)-strikes(i));
    end
end
beqCalls = calls(:,4);

% MAXIMUM ENTROPY MATRICES - PUTS
strikes = puts(:,2);
% EQUALS
priceSpace = repmat(prices,length(strikes),1);
AeqPuts = [];
for i = 1:length(strikes)
    for j = 1:length(priceSpace)
        AeqPuts(i,j) = max(0, strikes(i) - priceSpace(i,j));
    end
end
beqPuts = puts(:,4);

% COMBINING PUTS AND CALLS
Aeq = [AeqCalls; AeqPuts; ones(1,length(prices))];
beq = [beqCalls; beqPuts; 1];

% Inequality
b = [ones(length(priceSpace),1);zeros(length(priceSpace),1)];
A = [eye(length(priceSpace)); -1*eye(length(priceSpace))];
% STARTING
x0 = normpdf(prices, spot, spot*.3)';
x0 = x0/sum(x0);
% FUNCTION
fun = @(x) x' * log(x);

% NON-LINEAR OPTIMIZATION
opts = optimset('Algorithm','sqp', 'MaxIter', 1000, 'MaxFunEvals', 1000, 'TolX',1e-16, 'TolCon', 1e-4);
x1 = fmincon(fun,x0,A,b,Aeq,beq,[],[],[], opts);

plot(prices, x1, 'b');
hold on;
plot([spot spot],[0 max(x1)], '--r')
axis([.5*spot, 1.5*spot, 0, max(x1)])
hold off;

targetPrice = 195;
[~, idx] = min(abs(prices-targetPrice));

probAbove = sum(x1(idx:end))









