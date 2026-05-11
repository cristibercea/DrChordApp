import { Box, TextField, MenuItem } from '@mui/material';

export default function FilterBar({ filters, setFilters }) {
  // Funcție generică pentru a actualiza orice câmp din filtru
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFilters((prevFilters) => ({...prevFilters, [name]: value,}));
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: { xs: 'column', md: 'row' },
        gap: 2,
        alignItems: 'center',
        justifyContent: 'space-between',
        width: '100%',
      }}
    >
      {/* 1. Bara de căutare (Search by Name) */}
      <Box sx={{ width: { xs: '100%', md: '33%' } }}>
        <TextField
          fullWidth
          size="small"
          name="search"
          value={filters.search}
          onChange={handleChange}
          label="Search songs by name..."
          variant="outlined"
        />
      </Box>

      {/* 2. Filtre și Ordonare */}
      <Box
        sx={{
          display: 'flex',
          flexDirection: { xs: 'column', sm: 'row' },
          gap: 2,
          width: { xs: '100%', md: 'auto' },
        }}
      >
        {/* Filtrare după Gen */}
        <TextField
          fullWidth
          size="small"
          name="genre"
          value={filters.genre}
          onChange={handleChange}
          label="Filter by genre..."
          variant="outlined"
          sx={{ minWidth: { sm: '150px' } }}
        />

        {/* Filtrare după Status Tabulatură */}
        <TextField
          select
          fullWidth
          size="small"
          name="hasTab"
          value={filters.hasTab}
          onChange={handleChange}
          label="Tab Status"
          variant="outlined"
          sx={{ minWidth: { sm: '180px' } }}
        >
          <MenuItem value="all">All Songs</MenuItem>
          <MenuItem value="yes">Tablature Ready</MenuItem>
          <MenuItem value="no">Needs Transcription</MenuItem>
        </TextField>

        {/* Sortare / Ordonare */}
        <TextField
          select
          fullWidth
          size="small"
          name="sortBy"
          value={filters.sortBy}
          onChange={handleChange}
          label="Sort By"
          variant="outlined"
          sx={{ minWidth: { sm: '180px' } }}
        >
          <MenuItem value="date_desc">Newest Added</MenuItem>
          <MenuItem value="date_asc">Oldest Added</MenuItem>
          <MenuItem value="name_asc">Name (A-Z)</MenuItem>
          <MenuItem value="name_desc">Name (Z-A)</MenuItem>
        </TextField>
      </Box>
    </Box>
  );
}