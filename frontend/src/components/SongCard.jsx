import { useNavigate } from 'react-router-dom';
import {Card, CardContent, CardActions, Typography, Button, Chip, Box, Divider} from '@mui/material';


export default function SongCard({ song, onDelete, onGenerateTab, onEdit }) {
  const navigate = useNavigate();
  const isGenerating = Boolean(song.isGenerating);
  const handleGenerate = async () => {await onGenerateTab(song.id)};
  const formattedDate = new Date(song.date_recorded).toLocaleDateString();
  const hasTab = song.has_tabs === true || String(song.has_tabs).toLowerCase() === 'true';

  return (
    <Card variant="outlined" sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Typography variant="h6" component="h3" fontWeight="bold" noWrap title={song.name}>
            {song.name}
          </Typography>
          <Chip
            label={hasTab ? 'Tab Ready' : 'No Tab'}
            color={hasTab ? 'success' : 'default'}
            size="small"
            sx={{ fontWeight: 'bold', textTransform: 'uppercase', fontSize: '0.7rem' }}
          />
        </Box>

        <Typography variant="body2" color="text.secondary">
          <Box component="span" fontWeight="fontWeightMedium" color="text.primary"> {song.genre} </Box>
          {' - Added '} {formattedDate}
        </Typography>
      </CardContent>

      <CardActions sx={{ flexDirection: 'column', px: 2, pb: 2, gap: 1 }}>
        {/* Main Action Button */}
        {hasTab ? (
          <Button fullWidth disableElevation
            variant="contained"
            color="primary"
            onClick={() => navigate(`/tabs/${song.id}`)}
          > View Tablature </Button>
        ) : (
          <Button fullWidth disableElevation
            variant="contained"
            color="warning"
            onClick={handleGenerate}
            disabled={isGenerating}
          > {isGenerating ? 'Generating...' : 'Generate Tab'} </Button>
        )}

        <Divider sx={{ width: '100%', my: 1 }} />

        {/* Secondary Actions */}
        <Box display="flex" justifyContent="space-between" width="100%" gap={1}>
          <Button variant="text" color="inherit" fullWidth onClick={() => onEdit(song)}> Edit </Button>
          <Button variant="text" color="error" fullWidth onClick={() => onDelete(song.id)}> Delete </Button>
        </Box>
      </CardActions>
    </Card>
  );
}