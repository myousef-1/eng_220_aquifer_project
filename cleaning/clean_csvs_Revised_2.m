% James Wauneka
% ENG 220
% CSV cleaner

function clean_csvs(kind, inFile)
% Cleans raw CSVs into the shared schema and saves them to data/clean/.
% Run from the repo root (the folder that contains "data").
%
% Every cleaned well/gage file starts with the same shared columns:
%   site_id, site_name, latitude, longitude, date, source
% so they can be stacked or joined later. (Aquifer sensitivity is a table of
% map polygons, not sites, so it has its own layout.)
%
%   clean_csvs                     % clean everything whose input file exists
%   clean_csvs('groundwater')      % USGS monthly groundwater levels
%   clean_csvs('aquifer')          % NM OSE aquifer tests
%   clean_csvs('nmbgmr')           % data2: NMBGMR groundwater levels
%   clean_csvs('sensitivity')      % data3: aquifer sensitivity polygons
%   clean_csvs('streamflow')       % data4: USGS Rio Puerco at Cuba gage (3 files)
%   clean_csvs('welllogs')         % data7: NM OSE wells with well logs
%
%   clean_csvs('nmbgmr', 'data/other.csv')       % any kind on a specific file
%   clean_csvs('streamflow', {chanFile, fieldFile, metaFile})

    if nargin < 1, kind = 'all'; end
    kind = lower(char(kind));

    cleanDir = fullfile('data', 'clean');
    if ~exist(cleanDir, 'dir'), mkdir(cleanDir); end

    % ---- Default input files (edit here if you rename anything)
    in.groundwater = fullfile('data', 'water_flow_data_sandoval_county_sources.csv');
    in.aquifer     = fullfile('data', 'ose_aquifer_test_wells.csv');
    in.nmbgmr      = fullfile('data', 'data2_groundwater_sandoval_county.csv');
    in.sensitivity = fullfile('data', 'data3_Aquifer_Sensitivity.csv');
    in.streamflow  = {fullfile('data', 'data4_channel-measurements.csv'), ...
                      fullfile('data', 'data4_field-measurements.csv'), ...
                      fullfile('data', 'data4_monitoring-location-metadata.csv')};
    in.welllogs    = fullfile('data', 'data7_Wells With Well Log Information.csv');

    % ---- Output files
    out.groundwater = fullfile(cleanDir, 'groundwater_levels_monthly.csv');
    out.aquifer     = fullfile(cleanDir, 'aquifer_tests.csv');
    out.nmbgmr      = fullfile(cleanDir, 'groundwater_levels_nmbgmr.csv');
    out.sensitivity = fullfile(cleanDir, 'aquifer_sensitivity.csv');
    out.streamflow  = fullfile(cleanDir, 'streamflow_measurements.csv');
    out.welllogs    = fullfile(cleanDir, 'well_logs.csv');

    kinds = fieldnames(in);
    if strcmp(kind, 'all')
        % Run every cleaner whose input is present; skip (don't crash) on the rest.
        for k = 1:numel(kinds)
            in.(kinds{k}) = resolve_input(in.(kinds{k}));
            files = cellstr(in.(kinds{k}));
            missingFiles = files(~cellfun(@(f) exist(f, 'file') == 2, files));
            if isempty(missingFiles)
                run_cleaner(kinds{k}, in.(kinds{k}), out.(kinds{k}));
            else
                fprintf('--- Skipping %s: not found: %s\n\n', kinds{k}, strjoin(missingFiles, ', '));
            end
        end
    elseif ismember(kind, kinds)
        if nargin < 2, inFile = in.(kind); end
        run_cleaner(kind, resolve_input(inFile), out.(kind));
    else
        error('Unknown kind "%s". Use one of: %s, or no argument.', kind, strjoin(kinds, ', '));
    end
end

function files = resolve_input(files)
    % If an expected file isn't there, look in the same folder for one that
    % ends with that name - e.g. "1794522657311_data7_Wells_....csv" from a
    % browser download - and use it if there is exactly one match.
    wasChar = ischar(files) || isstring(files) && isscalar(files);
    files = cellstr(files);
    for k = 1:numel(files)
        if exist(files{k}, 'file') == 2, continue; end
        [folder, name, ext] = fileparts(files{k});
        hits = dir(fullfile(folder, ['*' name ext]));
        hits = hits(~[hits.isdir]);
        if numel(hits) == 1
            fprintf('Using "%s" for "%s"\n', hits(1).name, [name ext]);
            files{k} = fullfile(folder, hits(1).name);
        elseif numel(hits) > 1
            fprintf('Several files match "*%s%s" - rename the one you want to "%s%s":\n  %s\n', ...
                name, ext, name, ext, strjoin({hits.name}, '\n  '));
        end
    end
    if wasChar, files = files{1}; end
end

function run_cleaner(kind, inFile, outFile)
    switch kind
        case 'groundwater', clean_groundwater(inFile, outFile);
        case 'aquifer',     clean_aquifer_tests(inFile, outFile);
        case 'nmbgmr',      clean_nmbgmr(inFile, outFile);
        case 'sensitivity', clean_sensitivity(inFile, outFile);
        case 'streamflow'
            inFile = cellstr(inFile);
            if numel(inFile) ~= 3
                error('streamflow needs 3 files: {channel, field, metadata}.');
            end
            clean_streamflow(inFile{1}, inFile{2}, inFile{3}, outFile);
        case 'welllogs',    clean_well_logs(inFile, outFile);
    end
end

%% ======================================================================
%% Groundwater levels (USGS)
%% ======================================================================
function clean_groundwater(inFile, outFile)
    fprintf('--- Groundwater levels ---\n');
    T = read_all_text(inFile);

    need = {'parameter_code','interval_type','parent_statistic_name', ...
            'monitoring_location_id','monitoring_location_name','y','x', ...
            'start_date','arithmetic_mean'};
    require_cols(T, need, inFile);

    keep = strtrim(T.parameter_code) == "72019" & ...
           lower(strtrim(T.interval_type)) == "month" & ...
           lower(strtrim(T.parent_statistic_name)) == "mean";
    T = T(keep, :);
    fprintf('Rows after filtering (expected 2673): %d\n', height(T));

    C = table();
    C.site_id        = clean_text(T.monitoring_location_id);   % A/B suffix wells stay separate
    C.site_name      = clean_text(T.monitoring_location_name);
    C.latitude       = to_num(T.y);
    C.longitude      = to_num(T.x);
    C.date           = to_date(T.start_date);
    C.source         = repmat("USGS", height(T), 1);
    C.depth_to_water_ft = to_num(T.arithmetic_mean);

    report_duplicates(C);
    write_clean(C, outFile);
end

%% ======================================================================
%% Aquifer tests (NM OSE)
%% ======================================================================
function clean_aquifer_tests(inFile, outFile)
    fprintf('--- Aquifer tests ---\n');

    % ---- CONFIG: output column -> candidate raw headers (normalized names).
    % If the script says a column is missing, add the right header here.
    % (Normalized = lowercase, non-alphanumerics become underscores.)
    map = {
      'site_id',            {'ose_pod_id'}
      'site_name',          {'alt_well_name'}
      'latitude',           {'latitude'}
      'longitude',          {'longitude'}
      'date',               {'test_date_start'}
      'formation',          {'formation_name'}
      'well_depth_ft',      {'well_depth_ft'}
      'screen_top_ft',      {'depth_to_top_of_screen_ft'}
      'screen_bottom_ft',   {'depth_to_bottom_of_screen_ft'}
      'depth_to_water_ft',  {'start_water_level_ft'}
      'pumping_rate_gpm',   {'pumping_rate_gpm'}
      'transmissivity_drawdown_ft2_per_day', {'transmissivity_drawdown_ft2pday'}
      'transmissivity_recovery_ft2_per_day', {'transmissivity_recovery_ft2pday'}
      'storativity',        {'storativity'}
      'specific_capacity_gpm_per_ft', {'specific_capacity_gpm_p_ft'}
      'hydraulic_conductivity_ft_per_day', {'horizontal_hydraulic_conductivity_ftpd'}
    };
    countyCol = {'county_name'};
    waterDateCandidates = {'start_water_level_date'};

    T = read_all_text(inFile);
    avail = T.Properties.VariableNames;

    % County filter
    cc = find_col(avail, countyCol, 'county');
    T = T(upper(strtrim(T.(cc))) == "SANDOVAL", :);
    fprintf('Sandoval rows (expected 179): %d\n', height(T));

    C = table();
    for i = 1:size(map, 1)
        out = map{i,1};
        src = find_col(avail, map{i,2}, out);
        v = T.(src);
        switch out
            case {'site_id','site_name'}
                C.(out) = clean_text(v);
            case 'date'
                C.(out) = to_date(v);
            case 'formation'
                C.(out) = clean_formation(v);
            otherwise
                C.(out) = to_num(v);
        end
    end

    % The test date and unknown-date handling (1/1/1900 means unknown)
    wd = find_col_optional(avail, waterDateCandidates);
    if ~isempty(wd)
        d = to_date(T.(wd));
        fprintf('START WATER LEVEL DATE unknown (1900) rows: %d (left blank, column not exported)\n', sum(isnat(d)));
    end

    C.source = repmat("NM OSE", height(C), 1);
    C = order_shared_first(C);

    % Note ambiguous Jan 1 dates
    isJan1 = ~isnat(C.date) & month(C.date) == 1 & day(C.date) == 1;
    fprintf('Tests dated January 1 (may be year-only): %d  -> kept\n', sum(isJan1));

    C = drop_empty_constant(C);

    if ismember('formation', C.Properties.VariableNames)
        fprintf('Unique formations after cleaning (review for leftover typos):\n');
        disp(unique(C.formation(~ismissing(C.formation))));
    end

    write_clean(C, outFile);
end

%% ======================================================================
%% data2: Groundwater levels (NM Bureau of Geology / NMBGMR)
%% ======================================================================
function clean_nmbgmr(inFile, outFile)
    fprintf('--- NMBGMR groundwater levels ---\n');
    T = read_all_text(inFile);

    need = {'pointid','easting','northing','utmdatum','altitude','county', ...
            'welldepth','completiondate','casingdiameter','casingdepth', ...
            'datemeasured','depthtowaterbgs','levelstatus','measurementmethod'};
    require_cols(T, need, inFile);
    fprintf('Raw rows (expected 456): %d\n', height(T));

    % County is spelled both "SANDOVAL" and "Sandoval" -> compare in upper case
    T = T(upper(strtrim(T.county)) == "SANDOVAL", :);
    fprintf('Sandoval rows: %d\n', height(T));

    % Coordinates are UTM (NAD83, zone 13N) -> convert to lat/lon
    datum = unique(upper(strtrim(T.utmdatum(~ismissing(T.utmdatum)))));
    if ~isequal(datum, "NAD83")
        warning('Unexpected UTM datum(s): %s. Lat/lon assumes NAD83 zone 13N.', strjoin(datum, ', '));
    end
    E = to_num(T.easting);
    N = to_num(T.northing);
    [lat, lon] = utm_to_latlon(E, N, 13);

    h = height(T);
    C = table();
    C.site_id            = clean_text(T.pointid);
    C.site_name          = repmat(string(missing), h, 1);   % this source has no well names
    C.latitude           = lat;
    C.longitude          = lon;
    C.date               = to_date(T.datemeasured);          % "2018-12-18T00:00:00" -> 2018-12-18
    C.source             = repmat("NMBGMR", h, 1);
    C.depth_to_water_ft  = to_num(T.depthtowaterbgs);        % "NULL" -> blank
    C.level_status       = clean_text(T.levelstatus);        % USGS-style codes, e.g. R = recently pumped, D = dry
    C.measurement_method = clean_text(T.measurementmethod);
    C.altitude_ft        = to_num(T.altitude);
    C.well_depth_ft      = to_num(T.welldepth);
    C.casing_depth_ft    = to_num(T.casingdepth);
    C.casing_diameter_ft = to_num(T.casingdiameter);
    C.completion_date    = to_date(T.completiondate);        % "8/12/1998" -> 1998-08-12

    check_in_sandoval(C);

    % Rows with no water level (all are status D = dry) can't be used as levels
    noLevel = isnan(C.depth_to_water_ft);
    if any(noLevel)
        fprintf('Rows with no depth to water: %d (status: %s) -> dropped\n', sum(noLevel), ...
            list_values(C.level_status(noLevel)));
        C = C(~noLevel, :);
    end

    % Casing diameters are ~0.3-0.6 ft; one well reports 41 (likely a units/typo error)
    bad = C.casing_diameter_ft > 5;
    if any(bad)
        ids = unique(C.site_id(bad));
        fprintf('Casing diameter > 5 ft (bad value) blanked for: %s\n', strjoin(ids, ', '));
        C.casing_diameter_ft(bad) = NaN;
    end

    % Water deeper than the well itself is physically suspicious -> flag, keep
    deep = C.depth_to_water_ft > C.well_depth_ft;
    for i = find(deep)'
        fprintf('  CHECK: %s on %s has %.2f ft to water but the well is %.0f ft deep\n', ...
            C.site_id(i), string(C.date(i)), C.depth_to_water_ft(i), C.well_depth_ft(i));
    end

    % Non-static readings (pumping, recently pumped, etc.) are kept but counted
    nonStatic = ~ismissing(C.level_status);
    fprintf('Readings with a level-status code (not a clean static level): %d -> kept, see level_status\n', sum(nonStatic));

    isJan1 = ~isnat(C.completion_date) & month(C.completion_date) == 1 & day(C.completion_date) == 1;
    fprintf('Completion dates on January 1 (may be year-only): %d -> kept\n', sum(isJan1));

    report_duplicates(C);
    write_clean(C, outFile);
end

%% ======================================================================
%% data3: Aquifer sensitivity polygons
%% ======================================================================
function clean_sensitivity(inFile, outFile)
    fprintf('--- Aquifer sensitivity ---\n');
    T = read_all_text(inFile);
    require_cols(T, {'objectid','sensitivity','shape_area','shape_length'}, inFile);

    C = table();
    C.polygon_id = to_num(T.objectid);

    % Spell the class names out and add a numeric rank for sorting/plotting
    raw   = upper(clean_text(T.sensitivity));
    codes = ["LESS", "MOD", "HIGH"];
    names = ["Less", "Moderate", "High"];
    [ok, rank] = ismember(raw, codes);
    if any(~ok)
        fprintf('Unrecognized sensitivity values (left blank): %s\n', ...
            list_values(raw(~ok)));
    end
    C.sensitivity = repmat(string(missing), height(T), 1);
    C.sensitivity(ok) = names(rank(ok));
    C.sensitivity_rank = nan(height(T), 1);
    C.sensitivity_rank(ok) = rank(ok);              % 1 = Less, 2 = Moderate, 3 = High

    % The layer is in geographic coordinates, so these are in degrees, not ft/m
    C.area_sq_deg    = to_num(T.shape_area);
    C.perimeter_deg  = to_num(T.shape_length);

    nDup = numel(C.polygon_id) - numel(unique(C.polygon_id));
    fprintf('Polygons (expected 613): %d   duplicate IDs: %d\n', height(C), nDup);
    for k = 1:numel(names)
        sel = C.sensitivity == names(k);
        fprintf('  %-9s %4d polygons, %5.1f%% of total area\n', names(k), sum(sel), ...
            100 * sum(C.area_sq_deg(sel)) / sum(C.area_sq_deg, 'omitnan'));
    end
    fprintf('Note: this file has no geometry or site IDs, so it cannot be joined to wells by itself.\n');

    write_clean(C, outFile, {'polygon_id'});
end

%% ======================================================================
%% data4: USGS stream gage (channel + field measurements + site metadata)
%% ======================================================================
function clean_streamflow(chanFile, fieldFile, metaFile, outFile)
    fprintf('--- Streamflow measurements ---\n');
    Ch = read_all_text(chanFile);
    F  = read_all_text(fieldFile);
    M  = read_all_text(metaFile);

    require_cols(Ch, {'x','y','monitoring_location_id','field_visit_id','measurement_number', ...
        'time','channel_flow','channel_flow_unit','channel_width','channel_width_unit', ...
        'channel_area','channel_area_unit','channel_velocity','channel_velocity_unit', ...
        'channel_location_distance','channel_location_direction','channel_stability', ...
        'channel_material','measurement_type'}, chanFile);
    require_cols(F, {'field_visit_id','parameter_code','value','unit_of_measure', ...
        'measurement_rated','control_condition'}, fieldFile);
    require_cols(M, {'id','monitoring_location_name'}, metaFile);

    % Units go into the column names, so make sure they really are constant
    check_unit(Ch.channel_flow_unit,     "ft^3/s", 'channel_flow');
    check_unit(Ch.channel_width_unit,    "ft",     'channel_width');
    check_unit(Ch.channel_area_unit,     "ft^2",   'channel_area');
    check_unit(Ch.channel_velocity_unit, "ft/s",   'channel_velocity');
    check_unit(Ch.channel_location_distance_unit, "ft", 'channel_location_distance');

    h = height(Ch);
    C = table();
    C.site_id   = clean_text(Ch.monitoring_location_id);
    C.site_name = repmat(string(missing), h, 1);
    [tf, loc] = ismember(C.site_id, clean_text(M.id));
    metaNames = clean_text(M.monitoring_location_name);
    C.site_name(tf) = metaNames(loc(tf));
    C.latitude  = to_num(Ch.y);
    C.longitude = to_num(Ch.x);

    % Times are UTC ("...+00:00"); convert to local NM time before taking the date
    [d, tLocal] = utc_to_local(Ch.time, 'America/Denver');
    C.date   = d;
    C.source = repmat("USGS", h, 1);
    C.time_local = tLocal;
    C.channel_name = clean_category(Ch.channel_name);             % "main"/"Main" -> "Main"

    C.measurement_number      = to_num(Ch.measurement_number);
    C.discharge_cfs           = to_num(Ch.channel_flow);
    C.width_ft                = to_num(Ch.channel_width);
    C.area_ft2                = to_num(Ch.channel_area);
    C.velocity_ft_per_s       = to_num(Ch.channel_velocity);
    C.distance_from_gage_ft   = to_num(Ch.channel_location_distance);
    C.location_from_gage      = clean_category(Ch.channel_location_direction);
    C.measurement_type        = clean_category(Ch.measurement_type);      % Wading / Other
    C.channel_stability       = clean_category(Ch.channel_stability);     % "Unspecified" -> blank
    C.channel_material        = clean_category(Ch.channel_material);
    C.channel_evenness        = clean_category(Ch.channel_evenness);
    C.horizontal_velocity     = clean_category(Ch.horizontal_velocity_description);
    C.vertical_velocity       = clean_category(Ch.vertical_velocity_description);
    C.longitudinal_velocity   = clean_category(Ch.longitudinal_velocity_description);

    % Join gage height (parameter 00065) from the field-measurement file by visit ID
    F = F(strtrim(F.parameter_code) == "00065", :);
    check_unit(F.unit_of_measure, "ft", 'gage height');
    fVisit = clean_text(F.field_visit_id);
    if numel(unique(fVisit)) < numel(fVisit)
        warning('Some field visits have more than one gage height; the first is used.');
    end
    [tf, loc] = ismember(clean_text(Ch.field_visit_id), fVisit);
    gh = to_num(F.value);
    rated = clean_category(F.measurement_rated);
    ctrl  = clean_category(F.control_condition);
    C.gage_height_ft      = nan(h, 1);
    C.measurement_rating  = repmat(string(missing), h, 1);
    C.control_condition   = repmat(string(missing), h, 1);
    C.gage_height_ft(tf)     = gh(loc(tf));
    C.measurement_rating(tf) = rated(loc(tf));
    C.control_condition(tf)  = ctrl(loc(tf));
    fprintf('Gage heights matched to %d of %d measurements (%d field rows)\n', sum(tf), h, height(F));

    % Sanity checks
    fprintf('Measurements (expected 10): %d   zero-flow visits: %d\n', h, sum(C.discharge_cfs == 0));
    Qcalc = C.area_ft2 .* C.velocity_ft_per_s;          % Q = A * V
    off = abs(Qcalc - C.discharge_cfs) > 0.1 * C.discharge_cfs & C.discharge_cfs > 0;
    for i = find(off)'
        fprintf('  CHECK: measurement %d: Q = %.3g cfs but A*V = %.3g\n', ...
            C.measurement_number(i), C.discharge_cfs(i), Qcalc(i));
    end
    nums = C.measurement_number(~isnan(C.measurement_number));
    gaps = setdiff(min(nums):max(nums), nums);
    if ~isempty(gaps)
        fprintf('Measurement numbers missing from the file: %s\n', mat2str(gaps));
    end

    C = drop_empty_constant(C);    % e.g. channel name is "Main" on every row
    report_duplicates(C);
    write_clean(C, outFile);
end

%% ======================================================================
%% data7: NM OSE wells with well-log information
%% ======================================================================
function clean_well_logs(inFile, outFile)
    fprintf('--- Well logs (NM OSE) ---\n');
    T = read_all_text(inFile);
    require_cols(T, {'pod_number','sub_basin','county','source','q64','q16','q4','sec','tws', ...
        'range','x','y','start_date','finish_date','log_file_date','borehole_depth', ...
        'depth_water_first_encountered','driller','license_number'}, inFile);

    % Drop the footnote row at the bottom ("* UTM location was derived from PLSS")
    pod = strtrim(T.pod_number);
    note = startsWith(pod, "*") | ismissing(pod) | pod == "";
    if any(note)
        fprintf('Footnote/blank rows dropped: %d\n', sum(note));
        T = T(~note, :);
    end

    T = T(upper(strtrim(T.county)) == "SA", :);     % SA = Sandoval
    fprintf('Sandoval wells (expected 6): %d\n', height(T));

    % The unnamed column holds "*" when the location came from PLSS, not GPS
    starCol = T.Properties.VariableNames(startsWith(T.Properties.VariableNames, 'var'));
    if ~isempty(starCol)
        fromPLSS = strtrim(T.(starCol{1})) == "*";     % blank -> false
    else
        fromPLSS = false(height(T), 1);
    end

    E = to_num(T.x);
    N = to_num(T.y);
    [lat, lon] = utm_to_latlon(E, N, 13);

    h = height(T);
    C = table();
    C.site_id   = clean_text(T.pod_number);              % "SJ  00809   " -> "SJ 00809"
    C.site_name = repmat(string(missing), h, 1);
    C.latitude  = lat;
    C.longitude = lon;
    C.date      = to_date(T.finish_date);                 % date the well was finished
    C.source    = repmat("NM OSE", h, 1);
    C.start_date              = to_date(T.start_date);
    C.log_file_date           = to_date(T.log_file_date);
    C.borehole_depth_ft       = to_num(T.borehole_depth);
    C.depth_to_first_water_ft = to_num(T.depth_water_first_encountered);
    C.water_source            = clean_text(T.source);    % " " -> blank
    C.sub_basin               = clean_text(T.sub_basin);
    C.plss_location           = build_plss(T);
    C.location_from_plss      = fromPLSS;
    C.utm_easting             = E;
    C.utm_northing            = N;
    C.driller                 = clean_text(T.driller);
    C.license_number          = clean_text(T.license_number);

    % Coordinates outside Sandoval County are typos -> blank lat/lon, keep UTM for fixing
    outside = check_in_sandoval(C);
    C.latitude(outside)  = NaN;
    C.longitude(outside) = NaN;

    % Date order: start <= finish <= log filed
    for i = find(C.date < C.start_date)'
        fprintf('  CHECK: %s finished (%s) before it started (%s)\n', C.site_id(i), string(C.date(i)), string(C.start_date(i)));
    end
    for i = find(C.log_file_date < C.start_date)'
        fprintf('  CHECK: %s log filed (%s) before drilling started (%s)\n', ...
            C.site_id(i), string(C.log_file_date(i)), string(C.start_date(i)));
    end

    % First water deeper than the borehole is impossible
    for i = find(C.depth_to_first_water_ft > C.borehole_depth_ft)'
        fprintf('  CHECK: %s first water %g ft is below borehole depth %g ft\n', ...
            C.site_id(i), C.depth_to_first_water_ft(i), C.borehole_depth_ft(i));
    end

    % Same license number but different driller spellings -> likely a typo
    lic = unique(C.license_number(~ismissing(C.license_number)));
    for k = 1:numel(lic)
        names = unique(C.driller(C.license_number == lic(k) & ~ismissing(C.driller)));
        if numel(names) > 1
            fprintf('  CHECK: license %s has different driller names: %s\n', lic(k), strjoin(names, ' | '));
        end
    end

    fprintf('Locations derived from PLSS (approximate, quarter-section center): %d\n', sum(fromPLSS));
    report_duplicates(C);
    write_clean(C, outFile);
end

%% ======================================================================
%% Helpers
%% ======================================================================
function T = read_all_text(file)
    if ~exist(file, 'file')
        found = dir(fullfile(fileparts(file), '*.csv'));
        if isempty(found)
            seen = '(no CSV files found in that folder)';
        else
            seen = strjoin({found.name}, ', ');
        end
        error(['Input file "%s" not found.\nMATLAB''s current folder is: %s\n' ...
               'CSVs in "%s": %s\nEither change the current folder to your repo root, ' ...
               'or pass the full path: clean_csvs(''nmbgmr'', ''C:\\full\\path\\file.csv'')'], ...
               file, pwd, fileparts(file), seen);
    end
    opts = detectImportOptions(file, 'Encoding', 'UTF-8', 'Delimiter', ',');
    opts.VariableNamingRule = 'preserve';
    opts = setvartype(opts, opts.VariableNames, 'string');   % read everything as text, convert ourselves
    T = readtable(file, opts);
    names = cellfun(@normalize_name, T.Properties.VariableNames, 'UniformOutput', false);
    for k = 1:numel(names)                                   % blank headers -> var14, etc.
        if isempty(names{k}) || startsWith(names{k}, 'var') && ~isnan(str2double(names{k}(4:end)))
            names{k} = sprintf('var%d', k);
        end
    end
    T.Properties.VariableNames = matlab.lang.makeUniqueStrings(names);
end

function n = normalize_name(s)
    s = regexprep(char(s), '[^\x20-\x7E]', '');   % drops BOM debris from the first header
    s = lower(s);
    s = regexprep(s, '[^a-z0-9]+', '_');
    n = regexprep(s, '^_+|_+$', '');
end

function require_cols(T, need, file)
    miss = setdiff(need, T.Properties.VariableNames);
    if ~isempty(miss)
        error('Missing columns in %s: %s\nFound: %s', file, strjoin(miss, ', '), ...
              strjoin(T.Properties.VariableNames, ', '));
    end
end

function c = find_col(avail, candidates, label)
    c = find_col_optional(avail, candidates);
    if isempty(c)
        error(['Could not find a raw column for "%s". Tried: %s\n' ...
               'Available columns: %s\nAdd the right name to the CONFIG block.'], ...
               label, strjoin(candidates, ', '), strjoin(avail, ', '));
    end
end

function c = find_col_optional(avail, candidates)
    c = '';
    for i = 1:numel(candidates)
        hit = find(strcmp(avail, candidates{i}), 1);
        if ~isempty(hit), c = avail{hit}; return; end
    end
end

function s = clean_text(v)
    s = regexprep(strtrim(string(v)), '\s+', ' ');
    s(s == "" | ismember(upper(s), ["NA","N/A","NULL","MISSING","NAN"])) = missing;
end

function s = clean_category(v)
    % Text categories: also treat "Unspecified"/"None"/"Unknown" as blank
    s = clean_text(v);
    s(ismember(upper(s), ["UNSPECIFIED","NONE","UNKNOWN"])) = missing;
    % Consistent capitalization: "main" and "Main" -> "Main"
    ok = ~ismissing(s);
    s(ok) = upper(extractBefore(s(ok), 2)) + extractAfter(s(ok), 1);
end

function s = clean_formation(v)
    s = upper(clean_text(v));
    % Known fixes: add more as you spot them in the printed unique list
    fixes = {
        'SAANDSTONE', 'SANDSTONE'
    };
    for i = 1:size(fixes, 1)
        s = replace(s, fixes{i,1}, fixes{i,2});
    end
    s = regexprep(s, '\s+', ' ');
    s = strtrim(s);
end

function x = to_num(v)
    % Text -> number. Blanks/placeholders -> NaN. Ranges ("11 to 21") -> midpoint.
    v = strtrim(string(v));
    x = nan(size(v));
    for i = 1:numel(v)
        s = v(i);
        if ismissing(s) || s == "", continue; end
        if ismember(upper(s), ["NA","N/A","NULL","MISSING","NAN","-999","-9999"]), continue; end
        s = erase(s, ",");
        % range: "11 to 21" or "11 - 21" (a leading minus is not a range)
        tok = regexp(char(s), '^\s*(-?[\d\.]+)\s*(?:[Tt][Oo]|-)\s*(-?[\d\.]+)\s*$', 'tokens', 'once');
        if ~isempty(tok)
            x(i) = mean([str2double(tok{1}), str2double(tok{2})]);
            fprintf('  Range "%s" -> midpoint %g\n', s, x(i));
        else
            x(i) = str2double(regexprep(char(s), '[^\d\.\-eE+]', ''));
        end
    end
end

function d = to_date(v)
    % Handles "11/12/2002 12:00:00 AM", "11/12/2002", and "2002-11-12" (optionally with a time).
    v = strtrim(string(v));
    d = NaT(size(v));
    for i = 1:numel(v)
        if ismissing(v(i)) || v(i) == "", continue; end
        s = char(v(i));
        t = regexp(s, '^(\d{1,2})/(\d{1,2})/(\d{4})', 'tokens', 'once');
        if ~isempty(t)
            d(i) = datetime(str2double(t{3}), str2double(t{1}), str2double(t{2}));
            continue
        end
        t = regexp(s, '^(\d{4})-(\d{2})-(\d{2})', 'tokens', 'once');
        if ~isempty(t)
            d(i) = datetime(str2double(t{1}), str2double(t{2}), str2double(t{3}));
        end
    end
    d.Format = 'yyyy-MM-dd';
    d(year(d) == 1900) = NaT;            % 1/1/1900 = unknown
end

function [d, hhmm] = utc_to_local(v, tz)
    % "2026-03-09 18:10:00+00:00" (UTC) -> local date + "HH:mm" local time
    v = strtrim(string(v));
    if any(~ismissing(v) & ~endsWith(v, "+00:00"))
        warning('Some times are not UTC (+00:00); they are treated as UTC anyway.');
    end
    core = regexprep(v, '^(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}:\d{2}).*$', '$1 $2');
    t = datetime(core, 'InputFormat', 'yyyy-MM-dd HH:mm:ss', 'TimeZone', 'UTC');
    t.TimeZone = tz;
    hhmm = string(t, 'HH:mm');
    hhmm(isnat(t)) = missing;
    d = dateshift(t, 'start', 'day');
    d.TimeZone = '';
    d.Format = 'yyyy-MM-dd';
end

function [lat, lon] = utm_to_latlon(E, N, zone)
    % UTM (northern hemisphere, GRS80/NAD83) -> decimal degrees. No toolbox needed.
    a = 6378137; f = 1/298.257222101; k0 = 0.9996;
    e2 = f*(2 - f); ep2 = e2/(1 - e2);
    x = E - 500000;
    M = N / k0;
    mu = M / (a*(1 - e2/4 - 3*e2^2/64 - 5*e2^3/256));
    e1 = (1 - sqrt(1 - e2)) / (1 + sqrt(1 - e2));
    p = mu + (3*e1/2 - 27*e1^3/32)*sin(2*mu) + (21*e1^2/16 - 55*e1^4/32)*sin(4*mu) ...
           + (151*e1^3/96)*sin(6*mu) + (1097*e1^4/512)*sin(8*mu);
    C1 = ep2*cos(p).^2;
    T1 = tan(p).^2;
    N1 = a ./ sqrt(1 - e2*sin(p).^2);
    R1 = a*(1 - e2) ./ (1 - e2*sin(p).^2).^1.5;
    D  = x ./ (N1*k0);
    lat = p - (N1.*tan(p)./R1) .* (D.^2/2 - (5 + 3*T1 + 10*C1 - 4*C1.^2 - 9*ep2).*D.^4/24 ...
          + (61 + 90*T1 + 298*C1 + 45*T1.^2 - 252*ep2 - 3*C1.^2).*D.^6/720);
    lon = (D - (1 + 2*T1 + C1).*D.^3/6 ...
          + (5 - 2*C1 + 28*T1 - 3*C1.^2 + 8*ep2 + 24*T1.^2).*D.^5/120) ./ cos(p);
    lat = rad2deg(lat);
    lon = (zone - 1)*6 - 180 + 3 + rad2deg(lon);
end

function outside = check_in_sandoval(C)
    % Rough Sandoval County bounding box; prints any site that falls outside it
    outside = ~isnan(C.latitude) & ~( C.latitude  >= 35.2   & C.latitude  <= 36.35 & ...
                                      C.longitude >= -107.7 & C.longitude <= -106.2 );
    ids = unique(C.site_id(outside));
    for k = 1:numel(ids)
        i = find(C.site_id == ids(k), 1);
        fprintf('  CHECK: %s is outside Sandoval County (%.4f, %.4f) - likely a coordinate typo\n', ...
            ids(k), C.latitude(i), C.longitude(i));
    end
end

function txt = list_values(s)
    % Unique values as "a, b, c" (missing shown as "blank")
    s = string(s);
    s(ismissing(s)) = "blank";
    txt = char(strjoin(unique(s), ', '));
end

function check_unit(u, expected, label)
    u = unique(strtrim(u(~ismissing(u) & strtrim(u) ~= "")));
    if ~isempty(u) && ~isequal(u, expected)
        error('Unexpected units for %s: %s (expected %s)', label, strjoin(u, ', '), expected);
    end
end

function p = build_plss(T)
    % e.g. "NE SW Sec 09 T22N R04W" (quarters listed smallest to largest)
    p = strings(height(T), 1);
    q = [clean_text(T.q64), clean_text(T.q16), clean_text(T.q4)];
    sec = clean_text(T.sec); tws = clean_text(T.tws); rng = clean_text(T.range);
    for i = 1:height(T)
        parts = q(i, ~ismissing(q(i, :)));
        if ~ismissing(sec(i)), parts(end+1) = "Sec " + sec(i); end %#ok<AGROW>
        if ~ismissing(tws(i)), parts(end+1) = "T" + tws(i); end    %#ok<AGROW>
        if ~ismissing(rng(i)), parts(end+1) = "R" + rng(i); end    %#ok<AGROW>
        p(i) = strjoin(parts, ' ');
    end
    p(p == "") = missing;
end

function C = order_shared_first(C)
    shared = {'site_id','site_name','latitude','longitude','date','source'};
    rest   = setdiff(C.Properties.VariableNames, shared, 'stable');
    C = C(:, [shared, rest]);
end

function C = drop_empty_constant(C)
    % Drop columns that are empty or identical in every row (never the shared ones)
    shared = {'site_id','site_name','latitude','longitude','date','source'};
    rest = setdiff(C.Properties.VariableNames, shared, 'stable');
    for k = 1:numel(rest)
        col = C.(rest{k});
        allBlank = all(ismissing(col));
        identical = ~any(ismissing(col)) && numel(unique(col)) <= 1;
        if allBlank || identical
            fprintf('Dropping empty/constant column: %s\n', rest{k});
            C.(rest{k}) = [];
        end
    end
end

function report_duplicates(C)
    key = C.site_id + "|" + string(C.date, 'yyyy-MM-dd');
    fprintf('Duplicate site/date rows: %d\n', numel(key) - numel(unique(key)));
    fprintf('Sites: %d\n', numel(unique(C.site_id)));
end

function write_clean(C, outFile, sortKeys)
    if nargin < 3, sortKeys = {'site_id','date'}; end
    sortKeys = sortKeys(ismember(sortKeys, C.Properties.VariableNames));
    if ~isempty(sortKeys), C = sortrows(C, sortKeys); end

    % Convert everything to text ourselves so blanks are truly blank
    % (never 0, NaN, or NaT) and dates are YYYY-MM-DD.
    W = table();
    for k = 1:width(C)
        name = C.Properties.VariableNames{k};
        col = C.(name);
        if isdatetime(col)
            s = string(col, 'yyyy-MM-dd');
            s(isnat(col)) = "";
        elseif islogical(col)
            s = repmat("", size(col));
            s(col) = "yes";
        elseif isnumeric(col)
            s = compose("%.10g", col);
            s(isnan(col)) = "";
        else
            s = string(col);
            s(ismissing(s)) = "";
        end
        W.(name) = s;
    end

    % Write the CSV ourselves (UTF-8, quote only fields with commas/quotes/newlines)
    M = table2array(W);
    needs = contains(M, [",", """", newline, char(13)]);
    M(needs) = """" + replace(M(needs), """", """""") + """";
    lines = join(M, ",", 2);

    fid = fopen(outFile, 'w', 'n', 'UTF-8');
    if fid < 0, error('Could not open "%s" for writing (is it open in Excel?).', outFile); end
    closer = onCleanup(@() fclose(fid));
    fprintf(fid, '%s\n', strjoin(W.Properties.VariableNames, ','));
    for i = 1:numel(lines)
        fprintf(fid, '%s\n', lines(i));
    end
    clear closer
    fprintf('Saved %d rows x %d columns -> %s\n\n', height(W), width(W), outFile);
end
