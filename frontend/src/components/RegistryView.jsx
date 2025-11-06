import { useEffect, useState } from "react";
import axios from "axios";
import {
  Grid, Card, CardContent, Typography, Button, Box, Chip,
} from "@mui/material";

const API_BASE = "http://localhost:8000";

export default function RegistryView() {
  const [gifts, setGifts] = useState([]);

  useEffect(() => {
    axios.get(`${API_BASE}/api/registries/1/items/`).then((res) => setGifts(res.data));
  }, []);

  const reserveGift = async (id, minutes = 60) => {
    try {
      await axios.post(`${API_BASE}/api/reservations/${id}`, {
        duration_minutes: minutes,
      });
      alert("Reserved for 1 hour!");
    } catch (e) {
      alert(e.response?.data?.detail || "Failed to reserve");
    }
  };

  const confirmPurchase = async (id) => {
    try {
      await axios.post(`${API_BASE}/api/reservations/${id}/confirm`);
      alert("Confirmed purchase!");
    } catch (e) {
      alert(e.response?.data?.detail || "Failed to confirm");
    }
  };

  return (
    <Box className="p-6">
      <Typography variant="h4" className="mb-6 font-bold">🎁 Gift Registry</Typography>
      <Grid container spacing={3}>
        {gifts.map((gift) => (
          <Grid item xs={12} sm={6} md={4} key={gift.id}>
            <Card className="shadow-lg rounded-xl hover:shadow-2xl transition">
              <CardContent>
                <Typography variant="h6">{gift.name}</Typography>
                <a href={gift.url} target="_blank" rel="noreferrer">
                  <Typography variant="body2" color="text.secondary">{gift.url}</Typography>
                </a>
                {gift.bought ? (
                  <Chip label="Bought" color="success" className="mt-3" />
                ) : (
                  <Box className="flex gap-2 mt-3">
                    <Button
                      variant="contained"
                      onClick={() => reserveGift(gift.id, 60)}
                    >
                      Reserve 1h
                    </Button>
                    <Button
                      variant="outlined"
                      onClick={() => confirmPurchase(gift.id)}
                    >
                      Confirm
                    </Button>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
