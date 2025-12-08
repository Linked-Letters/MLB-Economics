#!/usr/bin/python
# Copyright (C) 2025 George Limpert
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>. 

import csv
import matplotlib as mpl
import matplotlib.pyplot as plt
import re
import scipy.stats as stats
import sys

def main ():
	# Get the parameters from the command line
	if len(sys.argv) < 3:
		print('Usage: '+sys.argv[0]+' <input file> <output image>')
		sys.exit(1)

	input_file = sys.argv[1].strip()
	output_file = sys.argv[2].strip()

	# Read in the CSV
	input_handle = open(input_file, newline = '', encoding = 'utf-8-sig')
	reader = csv.reader(input_handle)
	input_data = list(reader)
	input_handle.close()
	input_data_header = input_data.pop(0)

	# Get the indexes of the important columns
	input_data_season_col = input_data_header.index('year')
	input_data_payroll_col = input_data_header.index('team payroll')
	input_data_wins_col = input_data_header.index('w')
	input_data_losses_col = input_data_header.index('l')

	# Parse the CSV data
	team_payroll_data = []
	for input_row in input_data:
		cur_season = int(re.sub('\\D+', '', input_row[input_data_season_col]))
		cur_payroll = int(re.sub('\\D+', '', input_row[input_data_payroll_col]))
		cur_wins = int(re.sub('\\D+', '', input_row[input_data_wins_col]))
		cur_losses = int(re.sub('\\D+', '', input_row[input_data_losses_col]))
		cur_winpct = float(cur_wins) / (cur_wins + cur_losses)
		team_payroll_data.append([cur_season, cur_payroll, cur_winpct])

	# Get a list of the seasons
	season_list = sorted(list(set([x[0] for x in team_payroll_data])))

	season_data = []
	season_data_keys = ['Season', 'Gini', 'Correlation', 'P-Value', 'Teams', 'Total Payroll', 'Mean Payroll']
	# Loop through each season
	for cur_season in season_list:
		# Get a list of team payrolls for that season
		season_payroll_list = sorted([x[1] for x in team_payroll_data if x[0] == cur_season])
		# Number of teams
		season_teams = len(season_payroll_list)
		# Total payroll during the season
		season_total_payroll = sum(season_payroll_list)
		# Average team payroll during the season
		season_mean_payroll = float(season_total_payroll) / season_teams
		# Calculate the Gini coefficient for the season
		cumulative_payroll = 0
		cumulative_equal_payroll = 0
		sum_cumulative_payroll = 0
		sum_cumulative_equal_payroll = 0
		for cur_team_payroll in season_payroll_list:
			cumulative_equal_payroll += season_mean_payroll
			cumulative_payroll += cur_team_payroll
			sum_cumulative_equal_payroll += cumulative_equal_payroll
			sum_cumulative_payroll += cumulative_payroll
		season_gini_coefficient = float(sum_cumulative_payroll) / sum_cumulative_equal_payroll
		# Calculate the correlation between payroll and winning percentage
		season_correlation = stats.pearsonr([x[1] for x in team_payroll_data if x[0] == cur_season], [x[2] for x in team_payroll_data if x[0] == cur_season])
		# Store the data
		season_data.append([cur_season, season_gini_coefficient, season_correlation.statistic, season_correlation.pvalue, season_teams, season_total_payroll, season_mean_payroll])

	# How does inequality (1 - Gini) relate to the correlation between payroll and winning percentage?
	gini_wincorr_correlation = stats.pearsonr([(1 - x[season_data_keys.index('Gini')]) for x in season_data], [x[season_data_keys.index('Correlation')] for x in season_data])

	# Print a team rating table with ranks and the various strength of record columns
	table_text = []
	table_header = ['Season', 'Gini', 'Corr.', 'Teams', 'Total Payroll', 'Mean Payroll']
	table_alignment = ['>', '', '', '', '', '']
	table_title = 'Gini Coefficient and Payroll-Win% Correlation by Season'
	table_subtitles = ['1 - Gini Coefficient -> Payroll-Win% Correlation r-Value: ' + '{:0.4f}'.format(gini_wincorr_correlation.statistic), '1 - Gini Coefficient -> Payroll-Win% Correlation p-Value: ' + '{:0.4f}'.format(gini_wincorr_correlation.pvalue)]
	table_header_frequency = 15
	cur_line = 0
	for cur_season_data in season_data:
		if (cur_line % table_header_frequency) == 0:
			table_text.append(table_header)
		table_line = []
		table_line.append('{:d}'.format(int(cur_season_data[season_data_keys.index('Season')])))
		table_line.append('{:0.4f}'.format(float(cur_season_data[season_data_keys.index('Gini')])) + ' ')
		table_line.append('{:0.4f}'.format(float(cur_season_data[season_data_keys.index('Correlation')])) + ' ')
		table_line.append('{:d}'.format(int(cur_season_data[season_data_keys.index('Teams')])))
		table_line.append('$' + '{:0,.0f}'.format(round(float(cur_season_data[season_data_keys.index('Total Payroll')]), 0)) + ' ')
		table_line.append('$' + '{:0,.0f}'.format(round(float(cur_season_data[season_data_keys.index('Mean Payroll')]), 0)) + ' ')
		table_text.append(table_line)
		cur_line = cur_line + 1
	# Calculate the widths of the columns, including the headers, in advance
	table_column_width = []
	for cur_column in range(0, len(table_header), 1):
		table_column_width.append(max([len(x[cur_column]) for x in table_text]))
	# Print the table
	print(table_title)
	for cur_subtitle in table_subtitles:
		print(cur_subtitle)
	for cur_line in range(0, len(table_text), 1):
		cur_line_text = ''
		for cur_column in range(0, len(table_header), 1):
			if cur_column > 0:
				cur_line_text += ' '
			cur_line_text += ('{:' + table_alignment[cur_column] + str(int(table_column_width[cur_column])) + 's}').format(table_text[cur_line][cur_column])
		print(cur_line_text)

	plot_season_list = [x[season_data_keys.index('Season')] for x in season_data]
	plot_gini_list = [x[season_data_keys.index('Gini')] for x in season_data]
	plot_correlation_list = [x[season_data_keys.index('Correlation')] for x in season_data]

	fig = plt.figure(figsize = (6.5, 5.5), dpi = 150)
	plt.rcParams['font.family'] = 'Verdana'
	mpl.rcParams['text.antialiased'] = True
	ax = plt.gca()
	min_gini = min(plot_gini_list)
	max_gini = max(plot_gini_list)
	gini_extra_space = (max_gini - min_gini) * 0.03
	ax.set_xlim([min(plot_season_list), max(plot_season_list)])
	ax.set_ylim([min_gini - gini_extra_space, max_gini + gini_extra_space])
	ax.set_title('MLB Gini Coefficient and Payroll-Win% Correlation by Season')
	ax.set_xlabel('Season')
	ax.tick_params(axis = 'x', labelrotation = 45)		
	ax.set_ylabel('Gini Coefficient')
	ax2 = ax.twinx()
	ax2.set_ylabel('Payroll-Win% Correlation')
	ax2.set_ylim([0.0, 1.0])
	ax.plot(plot_season_list, plot_gini_list, color = (1, 0, 0, 1), label = 'Gini Coefficient')
	ax2.plot(plot_season_list, plot_correlation_list, color = (0, 0.7, 0.7, 1), label = 'Payroll-Win% Correlation')
	fig.legend(loc = 'center left', bbox_to_anchor = (0.65, 0.88), fancybox = True, prop = {'size': 6})
	plt.tight_layout()
	plt.savefig(output_file, bbox_inches = 'tight', dpi = 150)
	plt.close()
	plt.clf()

if __name__ == '__main__':
	main()
